from src import utils
import os
from pathlib import Path

def _df_to_list_county(df, county):
    '''
    get data from data frame to the result in array for 12 months for the input county
    @param
    df: input dataframe
    county: name of the county
    '''
    assert isinstance(county, str)
    Counties = ['Alameda','Alpine','Amador','Butte','Calaveras','Colusa','Contra Costa','Del Norte','El Dorado','Fresno','Glenn','Humboldt','Imperial','Inyo','Kern','Kings','Lake','Lassen','Los Angeles','Madera','Marin','Mariposa','Mendocino','Merced','Modoc','Mono','Monterey','Napa','Nevada','Orange','Placer','Plumas','Riverside','Sacramento','San Benito','San Bernardino','San Diego','San Francisco','San Joaquin','San Luis Obispo','San Mateo','Santa Barbara','Santa Clara','Santa Cruz','Shasta','Sierra','Siskiyou','Solano','Sonoma','Stanislaus','Sutter','Tehama','Trinity','Tulare','Tuolumne','Ventura','Yolo','Yuba']
    assert county in Counties
    ct_df = df[df['County']==county]
    ret = np.zeros(12)
    for i in range(12):
        if (i+1) in list(ct_df.month):
            ret[i] = ct_df[ct_df['month'] == i+1]['size']
    return ret


def test_county_prediction():
    '''
    test the prediction result from the county
    take all the data before 2020 for training and take the data from 2020 for testing
    the result is shown in mean absolute deviation and confusion matrix (happen or not)
    '''
    path = os.Path(os.getcwd()).parent.absolute()
    file_name = os.path.join(path, 'data/fire_occurrances_data.csv')
    df = pd.read_csv(file_name)
    test_df = df[df['year']==2020]
    
    # Mean absolute deviation
    MAD = 0
    for county in Counties:
        truth = _df_to_list_county(test_df, county)
        pred = utils.get_single_CountyPrediction(county, mode='eval')
        MAD += sum(abs(np.array(pred)-truth))/len(truth)
    MAD = MAD/len(Counties)
    
    # confusion matrix
    conf_mat = np.zeros((2,2))
    for county in Counties:
        truth = _df_to_list_county(test_df, county)
        pred = get_single_CountyPrediction(county, mode='eval')
        temp = np.bincount(np.array(truth > 0).astype(int) * 2 + (np.array(pred)  > 0).astype(int))
        sum_res = np.zeros(4)
        sum_res[:len(temp)] = temp
        conf_mat += sum_res.reshape(2,2)
    conf_mat = (conf_mat.T / np.sum(conf_mat, axis=1)).T
    # print(f'mean absolute deviation: {MAD}, conf_mat: {conf_mat}')
    return MAD, conf_mat