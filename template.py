import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
import pw
import pandas as pd
import spotifyFunctions as sf


from sklearn import preprocessing
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

from bokeh.plotting import figure, output_file, show, ColumnDataSource, save
from bokeh.embed import file_html
from bokeh.resources import CDN
from bokeh.transform import factor_cmap
from bokeh.palettes import all_palettes
from bokeh.models import HoverTool

client_id = pw.client_id
client_secret = pw.client_secret
redirect_uri = pw.redirect_uri
user_id = pw.user_id
username = pw.username

token = sf.auth(user_id, client_id, client_secret, redirect_uri)
sp = spotipy.Spotify(auth=token)


playlists = pd.DataFrame.from_dict(sf.getPlaylists('kocza.milan', token))

tracks = pd.DataFrame.from_dict(sf.getTracks('4tEeo0kzKunhBwsPYndOBz', token))


features = ['acousticness', 'danceability', 'instrumentalness', 'loudness', 'speechiness', 'valence', 'tempo']
loudness = tracks[["loudness"]].values
loudness_scaled = preprocessing.minmax_scale(loudness)

tempo = tracks[["tempo"]].values
tempo_scaled = preprocessing.minmax_scale(tempo)

tracks['loudness'] = pd.DataFrame(loudness_scaled)
tracks['tempo'] = pd.DataFrame(tempo_scaled)
x = tracks.loc[:, features].values

##############################################################################
#let's define the number of clusters with sum of squared distances method
sum_of_squared_distances = []
K = range(1,15)
for k in K:
    km = KMeans(n_clusters=k, random_state=0)
    km = km.fit(x)
    sum_of_squared_distances.append(km.inertia_)
    
#sum_of_squared_distances
##############################################################################
#let's define the number of clusters with Average silhouette method
silhouette_scores = []
for n_clusters in range(2,15):
    clusterer = KMeans (n_clusters=n_clusters)
    preds = clusterer.fit_predict(x)
    centers = clusterer.cluster_centers_

    score = silhouette_score (x, preds, metric='euclidean')
    silhouette_scores.append(score)
    #print ("For n_clusters = {}, silhouette score is {})".format(n_clusters, score)) 
    
###############################################################################
#plot elbow chart
K = range(1,15)
tooltips = [
        ("(x,y)", "($x, $y)")       
        ]

p = figure(plot_width=500, plot_height=400, tooltips=tooltips, title = 'Elbow method')

p.line(K, sum_of_squared_distances)
p.xaxis.axis_label = 'nr of clusters'
p.yaxis.axis_label = 'sum of squared distances'

show(p)

###############################################################################
#plot Average silhouette method chart
K = range(2,15)
tooltips = [
        ("(x,y)", "($x, $y)")       
        ]

p = figure(plot_width=500, plot_height=400, tooltips=tooltips, title = 'Average Silhouette Method')

p.line(K, silhouette_scores)
p.xaxis.axis_label = 'nr of clusters'
p.yaxis.axis_label = 'avg silhouette score'

show(p)

###############################################################################

#Clustering
n_clusters = 3

kmeans = KMeans(n_clusters=n_clusters)
kmeans.fit(x)
y_kmeans = kmeans.predict(x)


#PCA
pca = PCA(n_components=2)
pcaComponents = pca.fit_transform(x)

print("Explained variance ratio: " + str(sum(pca.explained_variance_ratio_)*100) + "%" )


pcadf = pd.DataFrame(data = pcaComponents, columns=['pca1', 'pca2'])
pcadf['label'] = y_kmeans
finaldf = pd.concat([pcadf, tracks[['albumName', 'albumImage', 'artisName', 'songTitle', 'songSample' ]]], axis=1)
finaldf['label'] = finaldf['label'].astype(str)
#finaldf.info()
###############################################################################

source = ColumnDataSource(data=dict(
    x = finaldf["pca1"],
    y = finaldf["pca2"],
    album = finaldf["albumName"],
    artist = finaldf["artisName"],
    title = finaldf["songTitle"],
    imgs = finaldf["albumImage"],
    category = finaldf["label"],
    sample = finaldf["songSample"]
))

tooltips = """
    <div>        
        <div>
            <p style="font-size: 12px; font-weight: bold;">
            <img src="@imgs" alt="@imgs" style="float:left; width:42px; height:42px; border=1 margin: 0px 15px 15px 0px;">
            @artist-@title </p>
        </div>
        
        <div>
            <audio controls>
                <source src="@sample" type="audio/mped">
            </audio>
        </div>          
    </div>
"""


palette = all_palettes['Accent'][4]
index_cmap = factor_cmap('category', palette = palette, factors=('0', '1'))
            
p = figure(plot_width=800, plot_height=600, tooltips=tooltips, title='Spotify Playlist Clustering')
p.circle("x", "y", size=22, alpha=0.8, source=source, legend='category', fill_color=index_cmap, hover_fill_color="darkgrey", hover_line_color="darkgrey" )

p.xaxis.axis_label = 'PCA1'
p.yaxis.axis_label = 'PCA2'
#p.background_fill_color = '#F5FBEF'
show(p)

HoverTool()