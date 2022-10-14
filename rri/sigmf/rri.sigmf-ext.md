# RRI Extension v1.0.0

The `rri` namespace extension defines Radio Research Instrument parameters extending the `global`, `captures`, and `annotations` objects in SigMF Recordings, and the `collection` object in a SigMF Collection.

REF: https://epop.phys.ucalgary.ca/data-handbook/rri-lv1-hdf-file/

The Level 1 dataset from the RRI is in HDF5 format and contains three major fields: `CASSIOPE Ephemeris`, `RRI Data`, and `RRI Settings`. This first version of the `rri` extension seeks only to map the minimally useful information to the SigMF recording metadata.  For example, most of the swept frequency fields are not mapped from HDF5 to SigMF as the current project that needs this converter is only looking at single frequency recordings.  Future versions may expand this. For this version of the `rri` extension, we are explicitly NOT including the `CASSIOPE Ephemeris` field which contains the timestamped Position, Velocity, and Attitude telemetry of the spacecraft during the time of the signal recording.  Future versions may include this information.

The RRI data set always contains two IQ streams.  The associated telemetry is for channel A or Channel B.  Therefore the mapping of the metadata from the HDF5 format to the SigMF metadata format requires a decision about which data is being mapped for which channel.  Therefore, some fields like

# SigMF Recordings

The following fields are specified for SigMF Recordings.

## 1 Global

The following names are specified in the `rri` namespace and should be used in the `global` object:

|name|required|type|unit|description|RRI HDF5|
|----|--------|----|----|-----------|--------|
|`experiment`    |true |string|N/A|Type of RRI Experiment|Not in HDF5 data, filename of downloaded data|
|`channel`       |true |string|N/A|Which RRI Channel, A or B|HDF5 contains metadata for each channel|
|`frequency`     |true |double|Hz |Center Frequency of Channel| `RRI Data: Channel A(orB) frequencies (Hz)`|
|`antenna_1_gain`|false|string|N/A|Gain of Channel 1 Radio Data|`RRI Settings:Antenna 1 Gain`|
|`antenna_2_gain`|false|string|N/A|Gain of Channel 2 Radio Data|`RRI Settings:Antenna 2 Gain`|
|`antenna_3_gain`|false|string|N/A|Gain of Channel 3 Radio Data|`RRI Settings:Antenna 3 Gain`|
|`antenna_4_gain`|false|string|N/A|Gain of Channel 4 Radio Data|`RRI Settings:Antenna 4 Gain`|
|`antenna_config`|false|string|N/A|Antenna Configuration, Monopole or Dipole|`RRI Settings:Antenna
|`format``       |false|string|N/A|Data Format|`RRI Settings:Data Format`|
|`bandwidth`     |false|double|Hz |Bandwidth of recording for A (or B)|`RRI Settings:Bandwidth A (kHz)`|

### `antenna_config` and `format`
The RRI can be configured to either be in a 4 monopole configuration or a dipole configuration. This is enabled by a physical relay switch on the instrument, and the `antenna_config` field essentially indicates the position of the relays.
Acceptable entries for `antenna_config`: `monopole` or `dipole`

Depending on the `format` object value, there can be a number of combinations of data in the 4 radio data channels. Common examples are below.

If in monopole configuration, a format value of `I1Q1I3Q3` indicates that complex data from monopoles 1 and 3 have been recorded. For this case, there will be two SigMF data files of complex datatype (`cf32_le`).

If in monopole configuration, a format value of `I1I2I3I4` indicates that real data from all 4 monopoles have been recorded. For this case, there will be 4 SigMF data files of real datatype (`rf32_le`).

If in dipole configuration, a format value of `I1Q1I3Q3` indicates that complex data from the two dipoles have been recorded.  For this case, there will be two SigMF data files of complex datatype (`cf32_le`).

For all of the above examples, appropriate mapping of associated RRI settings fields will be indicated.  For example, if only monopoles 1 and 3 are recorded in complex format, the `antenna_1_gain` and `antenna_3_gain` data will be mapped to the appropriate SigMF metadata files and the other two gain fields will be ignored.

For the initial development of the tool, only data in `dipole` mode is being considered. Care must be taken if using the associated converter for other antenna configurations (future work will vet the converter against multiple antenna configurations).

## 2 Captures

`rri` does not extend [Captures](https://github.com/gnuradio/SigMF/blob/master/sigmf-spec.md#captures-array).
The `core:samp_start`, `core:frequency`, and `core:datetime` fields are populated from the RRI data.
Note that the `core:datetime` field is populated from the first timestamp in the HDF5 `CASSIOPE Ephemeris:Ephemeris MET (seconds since May 24, 1968)` data, but converted from Mission Elapsed Time (MET) to UTC.

Future versions may revisit this and provide sample index, frequency, and timestamp in the `captures` field for each timestamp in the CASSIOPE metadata, 1 entry per second.  For now, this information can be inferred from sample rate information and timestamp for the first sample in the stream.  Future versions may also include satellite position, velocity, and attitude information from the `CASSIOPE Ephemeris` HDF5 object (though this might be more appropriate as an `annotations` object).

## 3 Annotations

`rri` does not extend [Annotations](https://github.com/gnuradio/SigMF/blob/master/sigmf-spec.md#annotations-array)

Future versions of this extensions may include satellite ephemeris information.  

## 4 Collection

`rri` does not extend SigMF Collections.

## 5 Examples

No `rri` examples (for now).
