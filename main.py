import bs4 as bs
import requests
import os
import csv
import re
ERR1="Sorry there was a problem ! :( Try restarting the program or check the internet connection."
LIST_LINK="data/mangalist.csv"
TEMP_FILE="data/mangalist_temp.csv"
if not os.path.exists(LIST_LINK):os.makedirs("data/")
def syntax_reminder():
    print("Syntax :")
    print("\t1) checkout <manga_name> # for searching and checking out mangas")
    print("\t2) exit # for exiting out at any point")
    print("\t3) refresh # to check if there are any updates to your selected manga lists")
def add(link):
    link1=link.replace("/manga/","/chapter/")
    print("Enter the initial chapter pointer to keep track :")
    looper=1
    while looper:
        chapter = input(">>>>> ")
        content=bs.BeautifulSoup(requests.get(link1+"/chapter_"+chapter).content,'html.parser')
        error_or_name=content.find_all('span',{'itemprop':'title'})[1].text.strip()
        if not error_or_name=="Error":
            fieldnames = 'name,link,recent_chapter'
            if os.path.isfile(LIST_LINK):
                with open(LIST_LINK, 'a') as mangalist:
                    mangalist.write("{},{},{}\n".format(error_or_name,link,chapter))
            else:
                with open(LIST_LINK, 'w') as mangalist:
                    mangalist.write(fieldnames+'\n')
                    mangalist.write("{},{},{}\n".format(error_or_name, link, chapter))
            print("Added : {} on chapter {}".format(error_or_name,chapter))
            looper=0
            refresh(error_or_name)
        else:
            print("Error.Please try again.")

def handler(item):
    manga_link=item.find('a').get('href')
    file_exists=os.path.isfile(LIST_LINK)
    has_manga=0
    if file_exists:
        with open(LIST_LINK,'r') as mangalist:
            list_=csv.reader(mangalist)
            next(list_)
            for row in list_:
                if row[1]==manga_link:
                    has_manga=row[0]
                    break
    if(has_manga):
        print(has_manga, " is already in your mangalist ! Redirecting to the refresh function")
        refresh(has_manga)
    else:
        content=bs.BeautifulSoup(requests.get(manga_link).content,'html.parser')
        print("."*60)
        print("\t{} selected :".format(item.text.strip()))
        ul=content.find('ul',{'class':"manga-info-text"})
        status=ul.find_all('li')[2].text[9:]
        print("This manga is",status)
        print("."*60)
        print("Some recent chapters are :")
        chapter_list=content.find('div',{'class':'chapter-list'})
        num_chapters=chapter_list.find_all('div')[:5]
        for i in range(0,len(num_chapters)):
            print(num_chapters[i].find('span').text)
        print("."*60)
        print("Add this manga to your list ? (Y/N):")
        answer=input(">>>>> ")
        if answer.upper()=="Y":
            add(manga_link)
def checkout(name):
    link="https://mangakakalot.com/search/"+name.replace(' ','_')
    #try:
    session = requests.get(link)
    if session.status_code==200:
        print("Searching .....",session.url)
        content=bs.BeautifulSoup(session.content,'html.parser')
        results=content.find_all('span',{'class':'item-name'})
        if results:
            n=1
            for result in results:
                print("\t{}.\t{}".format(n,result.text.strip()))
                n+=1
            if n==2:
                handler(results.pop())
            else:
                runchoice=1
                while(runchoice):
                    #try:
                    print("Which one of them?(Use Symbol Number):")
                    choice=int(input(">>>>> "))
                    handler(results[choice-1])
                    runchoice=0
                    #except ValueError as v:
                       # print("Enter a valid integer.")
                    #except IndexError as i:
                        #print("Enter Numbers within range.")
        else:
            print("No results found for :",name)
    else:
        print("Sorry there was a problem connecting to the website :( Try again with valid query")
    #except:
       #print(ERR1)

def download_and_reset(link_ref,chapter_num_list,row):
    print(f"Do you want to download all these chapters and set new pointer to Chapter {chapter_num_list[0]}?")
    answer=input(">>>>> ")
    if answer.upper()=="Y":
        with open(TEMP_FILE, 'a') as tempfile:
            tempfile.write(f"{row[0]},{row[1]},{chapter_num_list[0]}\n")
        for chapter in chapter_num_list:
            print(f"Downloading ....... Chapter {chapter}")
            content=bs.BeautifulSoup(requests.get(link_ref+chapter).content,'html.parser')
            images=content.find('div',{'class':'vung-doc'}).find_all('img')
            links=[x.attrs['src'] for x in images]
            counter=0
            name=re.sub('\W+','', row[0])
            if not os.path.exists('manga'):os.makedirs("manga")
            if not os.path.exists(f'manga/{name}'):os.makedirs(f"manga/{name}")
            if not os.path.exists(f'manga/{name}/Chapter {chapter}'):os.makedirs(f'manga/{name}/Chapter {chapter}')
            for link in links:
                with open(f"manga/{name}/Chapter {chapter}/{counter}.jpg",'wb') as file:
                    file.write(requests.get(link).content)
                counter+=1
    else:
        with open(TEMP_FILE, 'a') as tempfile:
            tempfile.write(f'{row[0]},{row[1]},{row[2]}\n')
def refresh(manga=False):
    if not os.path.isfile(LIST_LINK):
        print("Sorry you do not have any lists yet!.. Use [checkout <manga_name>] to search and create a list")
        return 0
    print("."*60)
    if manga:
        with open(TEMP_FILE,'w') as f:
            f.write("name,link,recent_chapter\n")
        with open(LIST_LINK, 'r') as mangalist:
            list_ = csv.reader(mangalist)
            next(list_)
            for row in list_:
                if row[0] == manga:
                    print(f"Refreshing and scraping out information for recent chapters for {manga}\n")
                    content = bs.BeautifulSoup(requests.get(row[1]).content, 'html.parser')
                    link_ref = row[1].replace("/manga/", "/chapter/") + "/chapter_"
                    chapters_list = content.find('div', {'class': 'chapter-list'}).select(f'a[href*={link_ref}]')
                    chapter_num_list = [x.attrs['href'][len(link_ref):] for x in chapters_list]
                    known_index = chapter_num_list.index(row[2])
                    if known_index == 0:
                        print(f"Other chapters for {manga} after Chapter {row[2]} haven't been released! Please checkout after sometime.")
                        with open(TEMP_FILE, 'a') as tempfile:
                            tempfile.write(f'{row[0]},{row[1]},{row[2]}\n')
                    else:
                        print("Other Chapters have been released !")
                        for x in range(0, known_index):
                            print(f"Chapter {chapter_num_list[x]}")
                        download_and_reset(link_ref, chapter_num_list[:known_index],row)
                else:
                    with open(TEMP_FILE, 'a') as tempfile:
                        tempfile.write(f'{row[0]},{row[1]},{row[2]}\n')
        os.remove(LIST_LINK)
        os.renames(TEMP_FILE, LIST_LINK)
    else:
        with open(TEMP_FILE,'w') as f:
            f.write("name,link,recent_chapter\n")
        with open(LIST_LINK, 'r') as mangalist:
            list_ = csv.reader(mangalist)
            next(list_)
            for row in list_:
                print(f"Refreshing and scraping out information for recent chapters for {row[0]}")
                content = bs.BeautifulSoup(requests.get(row[1]).content, 'html.parser')
                link_ref = row[1].replace("/manga/", "/chapter/") + "/chapter_"
                chapters_list = content.find('div', {'class': 'chapter-list'}).select(f'a[href*={link_ref}]')
                chapter_num_list = [x.attrs['href'][len(link_ref):] for x in chapters_list]
                known_index = chapter_num_list.index(row[2])
                if known_index == 0:
                    print(
                        f"Other chapters for {row[0]} after Chapter {row[2]} haven't been released! Please checkout after sometime.\n")
                    with open(TEMP_FILE, 'a') as tempfile:
                        tempfile.write(f'{row[0]},{row[1]},{row[2]}\n')
                else:
                    print("Other Chapters have been released !")
                    for x in range(0, known_index):
                        print(f"Chapter {chapter_num_list[x]}")
                    download_and_reset(link_ref, chapter_num_list[:known_index],row)
        os.remove(LIST_LINK)
        os.renames(TEMP_FILE, LIST_LINK)
if __name__=="__main__":
    print("Welcome !")
    syntax_reminder()
    while(1):
        input_=input('>>>>> ')
        if input_.strip()=="exit":
            break
        elif input_.strip()=="refresh":
            refresh()
        elif input_[:9]=="checkout ":
            checkout(input_[9:].strip().lower())
        else:
            print("Syntax Error :(")
            syntax_reminder()