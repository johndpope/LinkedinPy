# LinkedinPy


## Installation:
```
pip install --upgrade pip
curl https://pyenv.run | bash
curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash
pyenv install 3.6.0
pyenv local 3.6.0
pip install --upgrade git+https://github.com/socialbotspy/SocialCommons.git
pip install -r requirements.txt
```

##  APIs:
  - [search and connect](#search-and-connect)
  - [search and endorse](#search-and-endorse)
  - [search 1st connects and save to db and connect](#search-1st-connects-and-save-to-db-and-connect)

### search and connect
 
It sends invite to your 2nd or 3rd degree connections fetched from linkedin search
 
```python

 session = LinkedinPy()

 with smart_run(session):
     session.search_and_connect(
                    query="founder",
                    connection_relationship_code="%5B%22S%22%5D",
                    city_code="%5B%22in%3A6508%22%5D",
                    school_code="%5B%2213497%22%5D"
                )
 ```
### search and endorse

It simply endorses your first connections fetched from linkedin search

```python

 session = LinkedinPy()

 with smart_run(session):
     session.search_and_endorse(
                    query="founder",
                    city_code="%5B%22in%3A6508%22%5D",
                    school_code="%5B%2213497%22%5D"
                )
 ```


### search 1st connects and save to db and connect

It's a API to backup already connected contacts to local DB(for old connections and connections not made through search_and_connect API)
 
```python

 session = LinkedinPy()

 with smart_run(session):
     session.search_1stconnects_and_savetodb(
                    query="founder",
                    city_code="%5B%22in%3A6508%22%5D",
                    school_code="%5B%2213497%22%5D"
                )
 ```

 
 
## How to run:

 -  modify `quickstart.py` according to your requirements
 -  `python quickstart.py -u <my_linkedin_username> -p <mypssword>`
