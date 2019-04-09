/** Copyright (C) 2017-2018 Project-ODE
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

package org.oceandataexplorer.engine.workflows

import java.io.File
import java.net.URI

import com.github.nscala_time.time.Imports._

import org.oceandataexplorer.engine.io.WavReader
import org.oceandataexplorer.engine.signalprocessing._
import org.oceandataexplorer.engine.signalprocessing.windowfunctions._
import WindowFunctionTypes.Periodic

/**
 * Class that provides a simple signal processing workflow without using Spark.
 *
 * @author Alexandre Degurse, Joseph Allemandou
 *
 * @param recordDurationInSec The duration of a record in the workflow in seconds
 * @param windowSize The size of the segments to be generated
 * @param windowOverlap The generated segments overlap
 * @param nfft The size of the fft-computation window
 * @param lowFreqTOL The low boundary of the frequency range to study for TOL computation
 * @param highFreqTOL The high boundary of the frequency range to study for TOL computation
 */


class ScalaBenchmarkWorkflow
(
  val recordDurationInSec: Float,
  val windowSize: Int,
  val windowOverlap: Int,
  val nfft: Int,
  val lowFreqTOL: Option[Double] = None,
  val highFreqTOL: Option[Double] = None
) {

  private val segmentationClass = Segmentation(windowSize, windowOverlap)
  private val hammingClass = HammingWindowFunction(windowSize, Periodic)
  private val hammingNormalizationFactor = hammingClass.densityNormalizationFactor()
  private val energyClass = Energy(nfft)

  if (recordDurationInSec < 1.0) {
    throw new IllegalArgumentException(
      s"Unsupported record size ($recordDurationInSec) for scala-only benchmark"
      + "must be higher or equal to 1.0 for TOL computation"
    )
  }

  /**
   * Function used to read wav files inside a scala workflow
   *
   * @param soundUri The URI to find the sound
   * @param soundSamplingRate Sound's samplingRate
   * @param soundChannels Sound's number of channels
   * @param soundSampleSizeInBits The number of bits used to encode a sample
   * @param soundStartDate The starting date of the sound file
   * @return The records that contains wav's data
   */
  def readRecords(
    soundUri: URI,
    soundSamplingRate: Float,
    soundChannels: Int,
    soundSampleSizeInBits: Int,
    soundStartDate: String
  ): Array[Record] = {
    val wavFile: File = new File(soundUri)
    val wavReader = new WavReader(wavFile)

    val startTime: Long = new DateTime(soundStartDate, DateTimeZone.UTC).instant.millis

    val recordSize = (recordDurationInSec * soundSamplingRate).toInt
    val chunks: Seq[Array[Array[Double]]] = wavReader.readChunks(recordSize)

    // drop last record if incomplete
    val completeChunks = if (chunks.head.head.length != chunks.last.last.length) {
      chunks.dropRight(1)
    } else {
      chunks
    }

    completeChunks.zipWithIndex
      .map{case (record, idx) =>
        (startTime + (1000.0f * idx * recordSize / soundSamplingRate).toLong, record)
      }.toArray
  }

  /**
   * Method computing TOLs over the calibrated records
   *
   * @param records Computed records containing (timestamp, welch, spl, calibrated sound)
   * @param soundSamplingRate Sound's sample rate
   * @return A Map containing the tols
   */
  def computeTol(
    records: Array[(Long, Array[Array[Double]], Array[Array[Double]], Array[Array[Double]])],
    soundSamplingRate: Float
  ) : Array[(Long, Array[Array[Double]], Array[Array[Double]], Array[Array[Double]])] = {
    val tolNfft = soundSamplingRate.toInt
    val tolWindowSize = soundSamplingRate.toInt
    val tolWindowOverlap = 0

    val tolSegmentationClass = Segmentation(tolWindowSize, tolWindowOverlap)
    val tolHammingClass = HammingWindowFunction(tolWindowSize, Periodic)
    val tolNormFactor = tolHammingClass.densityNormalizationFactor()
    val tolFftClass = FFT(tolNfft, soundSamplingRate)
    val tolPeriodogramClass = Periodogram(
      tolNfft, 1.0 / (soundSamplingRate * tolNormFactor), soundSamplingRate)
    val tolClass = TOL(tolNfft, soundSamplingRate, lowFreqTOL, highFreqTOL)

    records
      .map{case (idx, welch, spl, calibratedChannels) => (idx, welch, spl,
        calibratedChannels.map(tolSegmentationClass.compute))}
      .map{case (idx, welch, spl, segmentedChannels) => (idx, welch, spl,
        segmentedChannels.map(_.map(tolHammingClass.applyToSignal)))}
      .map{case (idx, welch, spl, windowedChannels) => (idx, welch, spl,
        windowedChannels.map(_.map(tolFftClass.compute)))}
      .map{case (idx, welch, spl, fftChannels) => (idx, welch, spl,
        fftChannels.map(_.map(tolPeriodogramClass.compute)))}
      .map{case (idx, welch, spl, psdChannels) => (idx, welch, spl,
        psdChannels.map(_.map(tolClass.compute)))}
      // average TOL by frequency bin
      .map{case (idx, welch, spl, tolChannels) => (idx, welch, spl,
        tolChannels.map(_.transpose.map(_.sum)))}
  }

  /**
   * Apply method for the workflow
   *
   * @param soundUri The URI to find the sound
   * @param soundSamplingRate Sound's soundSamplingRate
   * @param soundChannels Sound's number of channels
   * @param soundSampleSizeInBits The number of bits used to encode a sample
   * @param soundCalibrationFactor The calibration factor for raw sound calibration
   * @param soundStartDate The starting date of the sound file
   * @return A map that contains all basic features as RDDs
   */
  def apply(
    soundUri: URI,
    soundSamplingRate: Float,
    soundChannels: Int,
    soundSampleSizeInBits: Int,
    soundStartDate: String = "1970-01-01T00:00:00.000Z",
    soundCalibrationFactor: Double = 0.0
  ): Array[
    (Long, Array[Array[Double]], Array[Array[Double]], Array[Array[Double]])
  ] = {

    val records = readRecords(
      soundUri,
      soundSamplingRate,
      soundChannels,
      soundSampleSizeInBits,
      soundStartDate)

    val soundCalibrationClass = SoundCalibration(soundCalibrationFactor)
    val fftClass = FFT(nfft, soundSamplingRate)
    val periodogramClass = Periodogram(
      nfft, 1.0/(soundSamplingRate*hammingNormalizationFactor), 1.0f)
    val welchClass = WelchSpectralDensity(nfft, soundSamplingRate)

    val welchSplCalibratedRecords = records
      .map{case (idx, calibratedChannels) => (idx, calibratedChannels,
        calibratedChannels.map(soundCalibrationClass.compute))}
      .map{case (idx, calibratedChannels, segmentedChannels) => (idx, calibratedChannels,
        segmentedChannels.map(segmentationClass.compute))}
      .map{case (idx, calibratedChannels, segmentedChannels) => (idx, calibratedChannels,
        segmentedChannels.map(_.map(hammingClass.applyToSignal)))}
      .map{case (idx, calibratedChannels, windowedChannels) => (idx, calibratedChannels,
        windowedChannels.map(_.map(fftClass.compute)))}
      .map{case (idx, calibratedChannels, fftChannels) => (idx, calibratedChannels,
        fftChannels.map(_.map(periodogramClass.compute)))}
      .map{case (idx, calibratedChannels, psdChannels) => (idx, calibratedChannels,
        psdChannels.map(welchClass.compute))}
      .map{case (idx, calibratedChannels, welchChannels) => (
        idx,
        welchChannels,
        Array(welchChannels.map(energyClass.computeSPLFromPSD)),
        calibratedChannels
      )}

    computeTol(welchSplCalibratedRecords, soundSamplingRate)
  }
}
