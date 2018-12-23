from requests_html import HTMLSession
import os
ERR1="Sorry there was a problem ! :( Try restarting the program or check the internet connection."
def syntax_reminder():
    print("Syntax :")
    print("\t1) checkout <manga_name> # for searching and checking out mangas")
    print("\t2) exit # for exiting out at any point")
    print("\t3) refresh # to check if there are any updates to your selected manga lists")
def handler(item):
    manga_link=item.links.pop()
    session=HTMLSession()
    r=session.get(manga_link)
    print("."*30)
    print("{} selected :".format(item.text))
    print("Some of the recent chapters:")
def checkout(name):
    session=HTMLSession()
    link="https://mangakakalot.com/search/"+name.replace(' ','_')
    try:
        r=session.get(link)
        if r.status_code==200:
            print("Searching .....",r.url)
            results=r.html.find(".item-name")
            if results:
                n=1
                for result in results:
                    print("\t{}.\t{}".format(n,result.text))
                    n+=1
                if n==2:
                    handler(results.pop())
                else:
                    runchoice=1
                    while(runchoice):
                        try:
                            print("Which one of them?(Use Symbol Number):")
                            choice=int(input(">>>>> "))
                            handler(results[choice-1])
                            runchoice=0
                        except ValueError as v:
                            print("Enter a valid integer.")
                        except IndexError as i:
                            print("Enter Numbers within range.")
            else:
                print("No results found for :",name)
        else:
            print("Sorry there was a problem connecting to the website :( Try again with valid query")
    except:
       print(ERR1)
def refresh():
    list_link="/data/mangalist.data"
    if os.path.isfile(list_link):
        with open(list_link,"wr"):
            print("yay")
    else:
        print("Sorry you do not have any lists yet!.. Use [checkout <manga_name> to search and create a list]")
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

            
