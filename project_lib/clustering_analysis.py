##############################
####### INITIAL CONFIG #######
##############################

# import required library to configure module
import pandas as pd
import numpy as np
from project_lib.initial_config import initial_settings
from project_lib.input_validation import validate_input_types, validate_dataframe_cols

# set the basic cofiguration for this module
initial_settings()

################################
####### MODULE FUNCTIONS #######
################################


def silhouette_inspection( 
    dataframe: pd.DataFrame,
    labels: pd.Series,
    model_name: str = None,
    display_figure: bool = True,
    save_fig: str = None
) -> dict:
    """      
    Plot silhouette score and shape for each cluster.
    
    Args
        dataframe: a dataframe with datapoints to calculate silhouette 
            according to sklearn.metrics.silhouette_samples and 
            sklearn.metrics.silhouette_score.
        labels: a Series or array with labels to calculate silhouette 
            according to sklearn.metrics.silhouette_samples and 
            sklearn.metrics.silhouette_score.
        model_name: a str with name to display on plot
        display_figure: a bool to indicate whether to plot silhouettes or not
        save_fig: a str with the path to save figure
        
    Return
        s_report: a dict with mean silhoutte 
            as well as silhouette per cluster.
    """   

    # input verification
    validate_input_types({"dataframe": dataframe}, (pd.core.frame.DataFrame,))
    validate_input_types({"labels": labels}, (pd.core.series.Series, np.ndarray,))
    if model_name is not None: 
        validate_input_types({"model_name": model_name}, (str,))
    validate_input_types({"display_figure": display_figure}, (bool,))
    if save_fig is not None:
        validate_input_types({"save_fig": save_fig}, (str,))

    # import required libraries
    from   sklearn.metrics   import silhouette_samples, silhouette_score
    import seaborn           as     sns
    import matplotlib.cm     as     cm
    import matplotlib.pyplot as     plt

    # instanciate a variable to save cluster sillhouettes
    s_report = {}

    # get number of clusters
    unique_clusters = set(labels)

    # create axs
    fig, ax = plt.subplots(nrows=1, ncols=1)

    # get average silhouette score the the given number of clusters
    s_score_mean = silhouette_score( 
        X=dataframe, 
        labels=labels, 
        metric='euclidean', 
        sample_size=None # use all datapoints
    )

    # add s mean to report
    s_report["s_mean"] = s_score_mean

    # set ax title, xlabel and ylabel
    if model_name is not None:
        plt.title(f'{model_name.upper()} mean silhouette: {s_score_mean:.3f}\n{model_name.upper()} number of clusters: {len(unique_clusters)}' )
    else:
        plt.title(f'Mean silhouette: {s_score_mean:.3f}\nNumber of clusters: {len(unique_clusters)}')
    plt.ylabel('Silhouette width proportional \nsamples in each cluster')
    plt.xlabel('Silhoutte Score')

    # calculate silhouette score for individual datapoints
    samples_silhouette_values = silhouette_samples( dataframe, labels )

    # Once the silhouette coefficient range from -1, 1
    ax.set_xlim( -0.2, 1 )
    # The (param + 1)*10 is to insert a blank space between silhouettes
    ax.set_ylim( [0, len(dataframe) + (len(unique_clusters) + 1) * 10] )

    # Plot a vertical line for average silhouette score of all the values
    ax.axvline( x = s_score_mean, color = "black", linestyle = "--")   

    # set the lower limit of the given silhouette
    y_lower = 10

    # iterate over silhouettes of the given cluster number
    for i in unique_clusters:
        # select datapoint of the i-th cluster 
        ith_cluster_samples = samples_silhouette_values[ labels == i ]

        # add cluster silhouette information
        s_report[f"cluster_{i}"] = dict(cluster_size=len(ith_cluster_samples))
        s_report[f"cluster_{i}"]["cluster_s_mean"] = ith_cluster_samples.mean()

        # sort datapoints according to silhouette sample values
        ith_cluster_samples.sort()

        # get the size of the i-th cluster -> number of instances
        ith_cluster_size = ith_cluster_samples.shape[0]

        # set the upper limit of the given silhouette
        y_upper = y_lower + ith_cluster_size

        # choose a color map
        cmap = cm.get_cmap( 'gist_rainbow' )
        # choose a color from color map
        color = cmap( i / len(unique_clusters) )

        # plot silhouette scores
        ax.fill_betweenx( np.arange( y_lower, y_upper ), # y coordinates
                            0, # first x curve
                            ith_cluster_samples, # second x curve
                            facecolor = color, 
                            edgecolor = 'black'
                        )

        # Compute the new y_lower for next plot
        y_lower = y_upper + 10

    # check if user wants to save figure
    if save_fig is not None:
        # save figure
        plt.savefig(save_fig, facecolor="white", bbox_inches="tight")

    # check if plot must be displayed
    if not display_figure:
        # don't display
        plt.close()

    return s_report        