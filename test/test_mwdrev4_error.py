import json
import numpy as np
import pandas as pd
from welleng.error import ErrorModel
from welleng.utils import get_sigmas

# Read validation data from file:
wd = json.load(open("test/test_data/error_mwdrev4_iscwsa_well_data.json"))
vd = json.load(open("test/test_data/error_mwdrev4_iscwsa_validation.json"))

df = pd.DataFrame(vd)


def get_md_index(error_data, md):
    i = np.where(error_data.survey_deg == md)[0][0]
    return i


# generate error model
err = ErrorModel(
    survey=wd['survey'],
    well_ref_params=wd['well_ref_params'],
    AzimuthRef=wd['well_ref_params']['AzimuthRef']
)


# initiate lists
def test_error_model_mwdrev4_iwcf(df=df, err=err):
    nn_c, ee_c, vv_c, ne_c, nv_c, ev_c = [], [], [], [], [], []
    data = [
        nn_c, ee_c, vv_c, ne_c, nv_c, ev_c
    ]

    # generate error data
    for index, row in df.iterrows():
        i = get_md_index(err, row['md'])
        s = row['source'].replace('-', '_')
        if s == "Totals":
            source_cov = err.errors.cov_NEVs.T[i]
        else:
            source_cov = err.errors.errors[s].cov_NEV.T[i]
        v = get_sigmas(source_cov, long=True)
        for j, d in enumerate(v):
            data[j].append(d)

    # convert to dictionary
    ed = {}
    headers = [
        'nn_c', 'ee_c', 'vv_c', 'ne_c', 'nv_c', 'ev_c'
    ]
    for i, h in enumerate(headers):
        ed[h] = data[i]

    df_c = pd.DataFrame(ed)

    df_r = df.join(df_c)

    headers = [
        'nn_d', 'ee_d', 'vv_d', 'ne_d', 'nv_d', 'ev_d'
    ]
    df_d = pd.DataFrame(
        np.around(
            np.array(df_c) - np.array(df.iloc[:, 2:]),
            decimals=4
        ),
        columns=headers
    )

    df_r = df_r.join(df_d)

    with np.errstate(divide='ignore', invalid='ignore'):
        error = np.nan_to_num(np.absolute(
            np.array(df_d) / np.array(df.iloc[:, 2:])
            ) * 100
        )

    assert np.all(error < 0.001)

    # if you wanted to view the results, this would save then to an Excel
    # file.
    # df_r.to_excel("test/test_data/error_mwdrev4_iscwsa_validation_results.xlsx")


if __name__ == '__main__':
    test_error_model_mwdrev4_iwcf(df=df, err=err)