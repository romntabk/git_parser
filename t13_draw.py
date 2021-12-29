# import cufflinks as cf
import plotly
import plotly.graph_objs as go
import numpy as np
from plotly.subplots import make_subplots
import pandas as pd
from t12 import git_parser
import argparse

def pie_data(df,series,year='-1'):
	if year=='-1':
		z = [str(i) for i in df['Data'] if len(i) !=0]
	else:
		z = [str(i['2021'])  for i in df['Data'] if len(i)!=0 and year in i ]
	
	c=[df['Rep'][i] for i in range(len(series)) if series[i]!=0]
	series = list(filter(lambda x: x!=0,series))
	pull=[]
	if len(series)!=0:
		pull = [0]*len(series)
		pull[list(series).index(max(series))] = 0.1
	return {'name': 'repository', 'values':series,'hovertext':z,'labels':c, 'pull':pull, 'hole':0.3}
def draw(data):
	# data =[('basic-data-collection-app', {'2020': 9}), ('basic-endpoint', {}), ('basic-vk-oauth-web-app', {'2020': 1}), ('basic_yandex_news_parser', {'2020': 2}), ('file-metadata-cpp', {}), ('Mob.dev', {}), ('OS_labs', {'2020': 10}), ('pydes', {}), ('python-exercises', {}), ('test-repo', {}), ('tgk_radio', {'2020': 102}), ('three.js', {}), ('timer', {'2019': 4}), ('triglinkiEvents', {'2021': 1}), ('visual_calc', {'2019': 1}), ('vk_3glinki_bot', {}), ('vk_bot_music_on_pc', {'2020': 5}), ('vk_tgk_bot_2', {'2020': 4}), ('wiki_parser', {'2019': 14}), ('youtube-dl', {})]
	
	df = pd.DataFrame(data , columns = ['Rep', 'Data'])
	series1=[sum(i.values()) if len(i)!=0 else 0 for i in df['Data'] ]
	series2=[i['2021'] if len(i)!=0 and '2021' in i.keys() else 0 for i in df['Data']]
	pie1=pie_data(df,series1)
	pie2=pie_data(df,series2,year='2021')
	fig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]])
	fig.add_trace(go.Pie(pie1),1,1)
	fig.add_trace(go.Pie(pie2),1,2)
	fig.update_layout(
	    title_text="GitHub commits",
	    # Add annotations in the center of the donut pies.
	    annotations=[dict(text='total', x=0.215, y=0.5, font_size=20, showarrow=False),
	                 dict(text='last_year', x=0.82, y=0.5, font_size=20, showarrow=False)])
	plotly.offline.plot(fig)

def main():
	parser=argparse.ArgumentParser()
	parser.add_argument('token')
	parser.add_argument('login')
	args=vars(parser.parse_args())
	token = args.get('token')
	login = args.get('login')
	git_p = git_parser(token)
	data= git_p.get_statistic(login)
	draw(data)

if __name__ =='__main__':
	main()