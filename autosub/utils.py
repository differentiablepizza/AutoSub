#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import sys
import shutil
import logger
from deepspeech import Model

_logger = logger.setup_applevel_logger(__name__)

def sort_alphanumeric(data):
    """Sort function to sort os.listdir() alphanumerically
    Helps to process audio files sequentially after splitting

    Args:
        data : file name
    """

    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]

    return sorted(data, key=alphanum_key)

def clean_folder(folder):
    """Delete everything inside a folder

    Args:
        folder : target folder
    """

    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            _logger.warn(f"Failed to delete {file_path}. Reason: {e}")

def get_model(args, arg_name):
    """Will prioritze supplied arguments but if not, try to find files

    Args:
        args : run-time arguments
        arg_name : either model or scorer file
    """
    
    if arg_name == 'model':
        arg_extension = '.pbmm'
    elif arg_name == 'scorer':
        arg_extension = '.scorer'

    arg = args.__getattribute__(arg_name)
    
    if arg is not None:
        model = os.path.abspath(arg)
        if not os.path.isfile(model):
            _logger.error(f"Supplied file {arg} doesn't exist. Please supply a valid {arg_name} file via the --{arg_name} flag")
            sys.exit(1)
    else:
        models = [file for file in os.listdir() if file.endswith(arg_extension)]
        num_models = len(models)
    
        if num_models == 0:
            _logger.warn(f"No {arg_name}s specified via --{arg_name} and none found in local directory. Please run getmodel.sh to get some")
            if arg_name == 'model':
                _logger.error("Must specify pbmm model")
                sys.exit(1)
            else:
                model = ''
        elif num_models != 1: 
            _logger.warn(f"Detected {num_models} {arg_name} files in local dir")
            if arg_name == 'model':
                _logger.error("Must specify pbmm model")
                sys.exit(1)
            else:
                _logger.warn("Please specify scorer using --scorer")
                model = ''
        else:
            model = os.path.abspath(models[0])                    
    
    _logger.info(f"{arg_name.capitalize()}: {model}")
    return(model)

def create_model(model, scorer):
    """Instantiate model and scorer

    Args:
        model : .pbmm model file
        scorer : .scorer file
    """

    try:
        ds = Model(model)
    except:
        _logger.error("Invalid model file")
        sys.exit(1)

    try:
        ds.enableExternalScorer(scorer)
    except:
        _logger.warn("Invalid scorer file. Running inference using only model file")
    return(ds)