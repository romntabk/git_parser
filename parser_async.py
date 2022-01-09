from github import Github
import requests
import os
import regex
import time
import logging
import asyncio
import json
import aiohttp
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
    

    async def do_request(self,session,url,to_json=True):
        try:
            async with session.get(url) as response:
                if to_json:
                    res = await response.read()
                    return json.loads(res.decode())
                return (response,url) # :D 
        except Exception as e:
            print(e)
            pass
    
    
    async def get_statistic(self, name):
        ''' async
        Keyword arguments:
            name -- user name on github
        
        list that contains tuples of the form 
        (repository name, dictionary of year - number of commits pairs)
        return    [repository name, {year_i : number of commits in year_i, ...}]
        returntype[       str     , {  str  :             int            , ...}]
        '''
        user = self.git.get_user(name)
        self.user_name=name
        url_branches = []
        for rep in user.get_repos():
            url = rep.branches_url[:-9]
            url_branches.append(url)
        tasks = []
        async with aiohttp.ClientSession(auth=aiohttp.BasicAuth(*self.auth)) as session:
            
            for url in url_branches:
                tasks.append(asyncio.create_task(self.do_request(session,url)))
            repos_branches = await asyncio.gather(*tasks)

            tasks=[]
            for index, branches in enumerate(repos_branches):
                tasks.append(asyncio.create_task(self._parse_branches(session,branches,user.get_repos()[index].name)))
            repos_branches_dicts = await asyncio.gather(*tasks)
        data = [(user.get_repos()[i].name, repos_branches_dicts[i]) for i in range(len(repos_branches_dicts))]
        return data#, f'LOG: uncheched_branches = {self.uncheched_branches}'
    
    async def check_first_commit(self,session,first_commit):
        link =first_commit[0].headers.get('Link')
        if link:
            page_url = link.split(',')[1].split(';')[0].split('<')[1].split('>')[0]
            return await self.do_request(session,page_url)
        return  await self.do_request(session,first_commit[1])

    async def _parse_branches(self,session,branches,rep):
        dict_ = {}#{'2019':12}
        urls = [] 
        last_shas = []
        
        for branche in branches:
            if isinstance(branche,dict) and 'commit' in branche and 'sha' in branche['commit']:
                last_sha = branche['commit']['sha'] 
                last_shas.append(last_sha)
                url_first_commit =  f'https://api.github.com/repos/{self.user_name}/{rep}/commits'
                urls.append(url_first_commit)
            

        tasks=[]
        for url in urls:
            tasks.append(asyncio.create_task(self.do_request(session,url,to_json=False)))
        first_commits = await asyncio.gather(*tasks) 
        
        urls = []      
        tasks=[]

        for first_commit in first_commits:
            tasks.append(asyncio.create_task(self.check_first_commit(session,first_commit)))
        
        first_commits = await asyncio.gather(*tasks)            
        
        for i,first_commit in enumerate(first_commits):
            first_sha=first_commit[-1]['sha']
            # print(first_sha)
            url_compare_sha = f'https://api.github.com/repos/{self.user_name}/{rep}/compare/{first_sha}...{last_shas[i]}'
            urls.append(url_compare_sha)
        
        tasks=[]
        for url in urls:
            tasks.append(asyncio.create_task(self.do_request(session,url)))
        compare_responses = await asyncio.gather(*tasks) 
        for compare_response in compare_responses:
            self._parse_branche(compare_response,dict_)    
        return dict_
    

    def _parse_branche(self,compare,dict_):
        bonus_create=1
        if not isinstance(compare,dict) or 'commits' not in compare:
            return 
        for i in compare['commits']:
            if isinstance(i.get('author'), dict) and 'login' in i['author']:
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
    nickname = 'mist-leet'
    git_p = git_parser(token)
    data=[]
    try:
        data= asyncio.get_event_loop().run_until_complete(git_p.get_statistic(nickname))
    except Exception as e:
        print(e)

    print(data)


if __name__ == '__main__':
    main() 
