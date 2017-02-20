#########################################################################
# Dicomifier - Copyright (C) Universite de Strasbourg
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
#########################################################################

import base64
import logging
import math
import itertools

import numpy
import odil

import odil_getter
import nifti_image
import meta_data
from .. import nifti
import siemens


def get_image(data_sets_frame_idx, dtype):
    """ Get the nifti image of the current stack
        :param data_sets_frame_idx: List containing the data sets of the frame 
                                    with the corresponding frame when it's a multiframe data set
        :param dtype: wanted type
        :return image: a nifti image
    """

    pixel_data_list = [get_pixel_data(data_set, frame_idx)
                       for data_set, frame_idx in data_sets_frame_idx]

    if dtype is None:
        has_float = any(x.dtype.kind == "f" for x in pixel_data_list)
        if has_float:
            dtype = numpy.float32
        else:
            # Assume all data sets have the same type
            dtype = pixel_data_list[0].dtype
        logging.info("dtype deduced to be: {}".format(dtype))

    pixel_data = numpy.ndarray(
        (len(data_sets_frame_idx),) + pixel_data_list[0].shape, dtype=dtype)
    for i, data in enumerate(pixel_data_list):
        pixel_data[i] = data

    dt = nifti.DT_UNKNOWN
    scanner_transform = numpy.identity(4)

    origin, spacing, direction = get_geometry(data_sets_frame_idx)

    if (len(data_sets_frame_idx) == 1 and
            "MOSAIC" in data_sets_frame_idx[0][0].as_string(odil.registry.ImageType)):
        data_set = data_sets_frame_idx[0][0]

        siemens_data = data_set.as_binary(odil.Tag("00291010"))[0]
        siemens_header = siemens.parse_csa(
            siemens_data.get_memory_view().tobytes())

        number_of_images_in_mosaic = siemens_header[
            "NumberOfImagesInMosaic"][0]
        tiles_per_line = int(math.ceil(math.sqrt(number_of_images_in_mosaic)))

        mosaic_shape = numpy.asarray(pixel_data.shape[-2:])

        rows = pixel_data.shape[-2] / tiles_per_line
        columns = pixel_data.shape[-1] / tiles_per_line

        real_shape = numpy.asarray([rows, columns])

        # Re-arrange array so that tiles are contiguous
        pixel_data = pixel_data.reshape(
            tiles_per_line, rows, tiles_per_line, columns)
        pixel_data = pixel_data.transpose((0, 2, 1, 3))
        pixel_data = pixel_data.reshape(tiles_per_line**2, rows, columns)

        # Get the origin of the tiles (i.e. origin of the first tile), cf.
        # http://nipy.org/nibabel/dicom/dicom_mosaic.html
        # WARNING: need to invert their rows and columns
        R = direction[:, :2]
        Q = R * spacing[:2]
        origin = origin + \
            numpy.dot(Q, (mosaic_shape[::-1] - real_shape[::-1]) / 2.)

        direction[:, 2] = siemens_header["SliceNormalVector"]

    samples_per_pix = data_sets_frame_idx[0][0].as_int("SamplesPerPixel")[0]

    if samples_per_pix == 1:
        lps_to_ras = [
            [-1,  0, 0],
            [0, -1, 0],
            [0,  0, 1]
        ]

        scanner_transform[:3, :3] = numpy.dot(lps_to_ras, direction)
        scanner_transform[:3, :3] = numpy.dot(
            scanner_transform[:3, :3], numpy.diag(spacing))
        scanner_transform[:3, 3] = numpy.dot(lps_to_ras, origin)

    elif samples_per_pix == 3 and data_sets_frame_idx[0][0].as_string("PhotometricInterpretation")[0] == "RGB":
        if dtype != numpy.uint8:
            raise Exception("Invalid dtype {} for RGB".format(dtype))
        dt = nifti.DT_RGB

    image = nifti_image.NIfTIImage(
        pixdim=[0.] + spacing + (8 - len(spacing) - 1) * [0.],
        cal_min=float(pixel_data.min()), cal_max=float(pixel_data.max()),
        qform_code=nifti.NIFTI_XFORM_SCANNER_ANAT,
        sform_code=nifti.NIFTI_XFORM_SCANNER_ANAT,
        qform=scanner_transform, sform=scanner_transform,
        xyz_units=nifti.NIFTI_UNITS_MM,
        data=pixel_data,
        datatype_=dt)

    return image


def get_pixel_data(data_set, frame_idx):
    """ Return the pixel data located in a dataset

        :param data_set: The dataset containing the pixelData 
        :param frame_idx: Index of the frame if data_set is multiframe, None otherwise
    """

    high_bit = data_set.as_int(odil.registry.HighBit)[0]

    byte_order = ">" if high_bit == 0 else "<"

    pixel_representation = 0
    if data_set.has(odil.registry.PixelRepresentation):
        pixel_representation = data_set.as_int(
            odil.registry.PixelRepresentation)[0]
    is_unsigned = (pixel_representation == 0)

    bits_allocated = data_set.as_int(odil.registry.BitsAllocated)[0]
    if bits_allocated % 8 != 0:
        raise NotImplementedError("Cannot handle non-byte types")

    dtype = numpy.dtype(
        "{}{}{}".format(
            byte_order, "u" if is_unsigned else "i", bits_allocated / 8))

    rows = data_set.as_int(odil.registry.Rows)[0]
    cols = data_set.as_int(odil.registry.Columns)[0]

    samples_per_pixel = data_set.as_int(odil.registry.SamplesPerPixel)[0]

    view = data_set.as_binary(odil.registry.PixelData)[0].get_memory_view()
    pixel_data = numpy.frombuffer(view.tobytes(), byte_order + dtype.char)
    if samples_per_pixel == 1:
        if data_set.has(odil.registry.NumberOfFrames):
            number_of_frames = data_set.as_int(odil.registry.NumberOfFrames)[0]
            pixel_data = numpy.asarray(pixel_data).reshape(
                number_of_frames, rows * cols)
            pixel_data = pixel_data[frame_idx, :]
            pixel_data = numpy.asarray(pixel_data).reshape(rows, cols)
        else:
            pixel_data = numpy.asarray(pixel_data).reshape(rows, cols)
    else:
        pixel_data = numpy.asarray(pixel_data).reshape(
            rows, cols, samples_per_pixel)

    # Mask the data using Bits Stored, cf. PS 3.5, 8.1.1
    bits_stored = data_set.as_int(odil.registry.BitsStored)[0]
    pixel_data = numpy.bitwise_and(pixel_data, 2**bits_stored - 1)

    # Rescale: look for Pixel Value Transformation sequence then Rescale Slope
    # and Rescale Intercept
    slope = None
    intercept = None
    if data_set.has(odil.registry.PixelValueTransformationSequence):
        transformation = data_set.as_data_set(
            odil.registry.PixelValueTransformationSequence)[0]
    else:
        transformation = data_set
    if transformation.has(odil.registry.RescaleSlope):
        slope = transformation.as_real(odil.registry.RescaleSlope)[0]
    if transformation.has(odil.registry.RescaleIntercept):
        intercept = transformation.as_real(odil.registry.RescaleIntercept)[0]
    if None not in [slope, intercept]:
        pixel_data = pixel_data * numpy.float32(slope) + numpy.float32(intercept)

    return pixel_data


def get_geometry(data_sets_frame_idx):
    """ Compute the geometry for the current stack

        :param data_sets_frame_idx: List containing the data sets of the frame 
                                    with the corresponding frame when it's a multiframe data set
    """

    default_origin = numpy.zeros((3,)).tolist()
    default_spacing = numpy.ones((3,)).tolist()
    default_direction = numpy.identity(3)

    data_set, first_idx = data_sets_frame_idx[0]

    # Here we look for image position - in the data_set or in the first frame
    if data_set.has(odil.registry.SharedFunctionalGroupsSequence):
        first_frame = data_set.as_data_set(
            odil.registry.PerFrameFunctionalGroupsSequence)[first_idx]
        shared = data_set.as_data_set(
            odil.registry.SharedFunctionalGroupsSequence)[0]
        if not first_frame.has(odil.registry.PlanePositionSequence):
            logging.info("No geometry found, default returned")
            return default_origin, default_spacing, default_direction
        else:
            plane_position_seq = first_frame.as_data_set(
                odil.registry.PlanePositionSequence)[0]
    else:
        plane_position_seq = data_set

    if plane_position_seq.has(odil.registry.ImagePositionPatient):
        # Here the orientation is correctly found
        origin = plane_position_seq.as_real(odil.registry.ImagePositionPatient)
    else:
        logging.info("No geometry found, default returned")
        return default_origin, default_spacing, default_direction

    # Here we look for image orientation - in data set or in the first frame
    if data_set.has(odil.registry.SharedFunctionalGroupsSequence):
        if first_frame.has(odil.registry.PlaneOrientationSequence):
            plane_orientation_seq = first_frame.as_data_set(
                odil.registry.PlaneOrientationSequence)[0]
        elif shared.has(odil.registry.PlaneOrientationSequence):
            plane_orientation_seq = shared.as_data_set(
                odil.registry.PlaneOrientationSequence)[0]
        else:
            logging.info("No orientation found, default returned")
            return origin, default_spacing, default_direction
    else:
        plane_orientation_seq = data_set

    if plane_orientation_seq.has(odil.registry.ImageOrientationPatient):
        orientation = plane_orientation_seq.as_real(
            odil.registry.ImageOrientationPatient)
    else:
        logging.info("No orientation found, default returned")
        return origin, default_spacing, default_direction

    direction = numpy.zeros((3, 3))
    direction[:, 0] = orientation[:3]
    direction[:, 1] = orientation[3:]
    direction[:, 2] = numpy.cross(direction[:, 0], direction[:, 1])

    # Here we try to find the PixelSpacing location if there is one
    if data_set.has(odil.registry.SharedFunctionalGroupsSequence):
        if shared.has(odil.registry.PixelMeasuresSequence):
            pixel_measures_sequence = shared.as_data_set(
                odil.registry.PixelMeasuresSequence)[0]
        else:
            if first_frame.has(odil.registry.PixelMeasuresSequence):
                pixel_measures_sequence = first_frame.as_data_set(
                    odil.registry.PixelMeasuresSequence)[0]
                ref_spacing = list(pixel_measures_sequence.as_real(
                    odil.registry.PixelSpacing))
                for data_set, frame_idx in data_sets_frame_idx[:1]:
                    spacing_ = list(
                        odil_getter._get_spacing(data_set, frame_idx))
                    if spacing_ != ref_spacing:
                        logging.warning(
                            "One or more frames found with different spacings")
                        break
            else:
                logging.info("No spacing found, default returned")
                return origin, default_spacing, direction
    else:
        pixel_measures_sequence = data_set
    spacing = list(pixel_measures_sequence.as_real(odil.registry.PixelSpacing))

    if len(data_sets_frame_idx) == 1:
        spacing.append(1.)
    else:
        # Here we try to find the position of the second frame (plane_position_seq)
        if data_set.has(odil.registry.SharedFunctionalGroupsSequence):
            second_data_set, second_frame_idx = data_sets_frame_idx[1]
            second_frame = second_data_set.as_data_set(
                odil.registry.PerFrameFunctionalGroupsSequence)[second_frame_idx]
            plane_position_seq = second_frame.as_data_set(
                odil.registry.PlanePositionSequence)[0]
        else:
            if data_set.has(odil.registry.SpacingBetweenSlices):
                spacing.append(data_set.as_real(
                    odil.registry.SpacingBetweenSlices)[0])
                return origin, spacing, direction
            else:
                plane_position_seq = data_sets_frame_idx[1][0]

        if plane_position_seq.has(odil.registry.ImagePositionPatient):
            second_position = plane_position_seq.as_real(
                odil.registry.ImagePositionPatient)
            difference = numpy.subtract(
                second_position,
                origin)
            spacing_between_slices = abs(
                numpy.dot(difference, direction[:, 2]))
            if spacing_between_slices != 0.0:
                spacing.append(spacing_between_slices)
            else:
                logging.info("Something went wrong when spliting/sorting frames, "
                             "two or more frames with the same position were found")
                spacing.append(1.)
        else:
            logging.info(
                "No position found for one or more frames, default spacing returned")
            spacing.append(1.)
    return origin, spacing, direction
