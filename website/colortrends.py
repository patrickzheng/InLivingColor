
import numpy as np
import matplotlib
matplotlib.use('Agg')


import matplotlib.pyplot as plt

from colorsys import hsv_to_rgb

from cassandra.cluster import Cluster


def getcolortrendsus_png(granularity='country/month',
                         state='*',
                         beginningyear='2005-01',
                         endingyear='2015-06'):


    # Connect to keyspace 'inlivingcolor'
    cluster = Cluster()
    session = cluster.connect('inlivingcolor')


    resp = session.execute("""
    select * from allhuecountsbatch
    where granularity = '%s'
    and country='United States'
    and region='%s'
    and locality='*'
    and county='*'
    and datetaken>='%s' and datetaken<='%s'
    """%(granularity,state,beginningyear,endingyear))
    # resp


    # In[131]:



    # In[132]:

    huesstrengths = np.array([row[7] for row in resp])
    counts = np.array([row[6] for row in resp])

    # Don't show the month actually, just the year
    months = [row[5][:4] for row in resp]
    # months = [row[5] for row in resp]


    # In[133]:

    def gaussian(x, mu, sig):
        return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))

    convhuestrengths = np.zeros_like(huesstrengths) * 0.0
    shifts = np.array([-3,-2,-1,0,1,2,3,])
    normalizingfactor = np.sum(gaussian(shifts,0,1))
    # normalizingfactor


    # In[134]:


    for i in shifts:
        convhuestrengths += gaussian(i,0,1)/normalizingfactor*np.roll(huesstrengths,i)

    convhuestrengths = np.roll(convhuestrengths,2,1)
    colors = np.roll([hsv_to_rgb(hue,1,0.75) for hue in (1.0/32+np.arange(16.0)/16.0)],2,0)

    convhuestrengths
    # gaussian(i,0,1)/normalizingfactor*np.roll(huesstrengths,i)


    # In[135]:

    plt.xkcd()
    fig = plt.figure(figsize=(20,12))

    # for i in range(16)[0:]:
    # for i in [0,1,5,6,]:
    # #     print i
    #     hue = float(i)/16.0+1.0/32
    #     plt.plot(convhuestrengths[:,i],'-',c=hsv_to_rgb(hue,1,0.75),label=int(hue*360))

    ax = fig.add_subplot(515)
    ax.yaxis.tick_right()
    plt.xticks(range(len(months))[::12], months[::12], size='small')
    plt.ylabel('# of Photos')
    plt.xlabel('Month')

    plt.plot(range(len(months))[::],counts,'b^',alpha=0.75,)



    ax = fig.add_subplot(514)
    ax.yaxis.tick_right()
    plt.xticks(range(len(months))[::12], months[::12], size='small')
    plt.ylabel('Percent')

    plt.stackplot(range(len(months))[::],convhuestrengths[:,:3].T,baseline='zero', alpha=0.75,
                  colors=colors[:3])


    ax = fig.add_subplot(513)
    ax.yaxis.tick_right()
    plt.xticks(range(len(months))[::12], months[::12], size='small')
    plt.ylabel('Percent')

    plt.stackplot(range(len(months))[::],convhuestrengths[:,3:5].T,baseline='zero', alpha=0.75,
                  colors=colors[3:5])


    ax = fig.add_subplot(512)
    ax.yaxis.tick_right()
    plt.xticks(range(len(months))[::12], months[::12], size='small')
    plt.ylabel('Percent')

    plt.stackplot(range(len(months))[::],convhuestrengths[:,5:9].T,baseline='zero', alpha=0.75,
                  colors=colors[5:9])

    ax = fig.add_subplot(511)
    ax.yaxis.tick_right()
    plt.xticks(range(len(months))[::12], months[::12],)
    plt.ylabel('Percent')

    plt.stackplot(range(len(months))[::],convhuestrengths[:,9:16].T,baseline='zero', alpha=0.75,
                  colors=colors[9:16])



    # plt.plot(counts,'k^',)
    # plt.legend(title='Hues (0-360)',bbox_to_anchor=(1.125, 1.0),
    #           ncol=1,)
    # plt.ylabel('Percent')
    plt.suptitle('Strengths of Hues in %s Flickr Images (%s to %s)'%( 'U.S.' if state is '*' else state,beginningyear,endingyear), fontsize=24)
    # for i,hue


    # In[138]:

    from cStringIO import StringIO

    output = StringIO()
    fig.savefig(output)
    contents = output.getvalue()

    return contents



