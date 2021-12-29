from github import Github
import requests
import os
import regex
import time
import logging


def timer1(f):
    def wrapper(*args):
        start = time.time()
        res = f(*args)
        print(f'Exectuion time - {time.time()-start}s')
        return res 
    return wrapper


class git_parser:
    def __init__(self,token = '',nickname='username'):
        '''
        Keyword arguments:
            token = '' -- github token
            nickname = 'username' -- nickname for authorized requests

            authorization is needed to increase 
            the limit of requests to the github api
        '''
        self.data = []
        self.auth=''
        self.uncheched_branches={}
        if len(token) < 5:
            self.git = Github()
        else:      
            self.auth = (nickname, token)
            self.git = Github (login_or_token=token)


    def get_statistic(self, name):
        '''
        Keyword arguments:
            name -- user name on github
        
        list that contains tuples of the form 
        (repository name, dictionary of year - number of commits pairs)
        return    [repository name, {year_i : number of commits in year_i, ...}]
        returntype[       str     , {  str  :             int            , ...}]
        '''
        user = self.git.get_user(name)
        arr=[]
        self.user_name=name
        for rep in user.get_repos():
            try:
                branches = requests.get(rep.branches_url[:-9],auth=self.auth,timeout=1000)
                rep_data=(rep.name,self._parse_branches(branches.json(),rep.name))
                self.data.append(rep_data)
            except:
                pass
            
        return self.data#, f'LOG: uncheched_branches = {self.uncheched_branches}'


    @timer1
    def _parse_branches(self,branches,rep):
        print(f'repository: {rep}',end=' ')
        dict_ = {}#{'2019':12}
        for branche in branches:
            try:
                print(f'branch:', branche['name'])
                last_sha = branche['commit']['sha'] 
                url_first_commit =  f'https://api.github.com/repos/{self.user_name}/{rep}/commits'
                first_commit = requests.get(url_first_commit, auth=self.auth,timeout=1000)
                link =first_commit.headers.get('Link')
                if link:
                     page_url = link.split(',')[1].split(';')[0].split('<')[1].split('>')[0]
                     # page_url2 = link.split(';')[0][1:-1] DOESNT WORK :C WHY :(
                     # first_commit2 =requests.get(page_url2,auth=self.auth).json() 
                     try:
                        first_commit = requests.get(page_url,auth=self.auth,timeout=1000)
                     except:
                        pass
                first_commit=first_commit.json()
                first_sha=first_commit[-1]['sha']
                url_compare_sha = f'https://api.github.com/repos/{self.user_name}/{rep}/compare/{first_sha}...{last_sha}'
                compare_response = requests.get(url_compare_sha, auth=self.auth,timeout=1000).json()
                self._parse_branche(compare_response,dict_)
            except:
                if rep in self.uncheched_branches:
                    self.uncheched_branches[rep]+=1
                else:
                    self.uncheched_branches[rep]=1
        return dict_
    

    def _parse_branche(self,compare,dict_):
        bonus_create=1
        for i in compare['commits']:
            if isinstance(i.get('author'), dict) :
                nick =i['author']['login']
            else:
                nick = i['commit']['author']['name']
            if nick == self.user_name:
                if i['commit']['author']['date'][:4] in dict_:
                    dict_[i['commit']['author']['date'][:4]] += 1+bonus_create
                else:
                    dict_[i['commit']['author']['date'][:4]] = 1+bonus_create
                bonus_create=0
    



def main():
    token = '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'
    nickname = 'romntabk'
    git_p = git_parser(token)
    data= git_p.get_statistic('mist-leet')
    print(data)


if __name__ == '__main__':
    main()
