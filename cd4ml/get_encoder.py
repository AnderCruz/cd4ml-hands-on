import os
import pickle
from cd4ml.filenames import get_model_files
from sklearn.preprocessing import OneHotEncoder
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def get_encoder_from_stream(stream, ml_fields, omit_cols=None):
    target = ml_fields['target_name']

    categorical = [k for k in ml_fields['categorical'].keys() if k != target]
    numerical = [f for f in ml_fields['numerical'] if f != target]

    df = pd.DataFrame(stream)

    if omit_cols:
        df = df.drop(columns=omit_cols, errors='ignore')

    encoder = OneHotEncoder(handle_unknown='ignore', sparse=False)

    encoder.fit(df[categorical])

    return {
        "encoder": encoder,
        "categorical": categorical,
        "numerical": numerical
    }


def get_trained_encoder(stream, ml_fields, problem_name, write=True,
                        read_from_file=False, base_features_omitted=None):

    file_names = get_model_files(problem_name)
    encoder_file = file_names.get('encoder')

    if encoder_file and os.path.exists(encoder_file) and read_from_file:
        logger.info(f'Reading encoder from: {encoder_file}')
        with open(encoder_file, "rb") as f:
            return pickle.load(f)

    logger.info('Building encoder')
    encoder = get_encoder_from_stream(
        stream, ml_fields, omit_cols=base_features_omitted
    )

    if write and encoder_file:
        logger.info(f'Writing encoder to: {encoder_file}')
        with open(encoder_file, "wb") as f:
            pickle.dump(encoder, f)

    return encoder