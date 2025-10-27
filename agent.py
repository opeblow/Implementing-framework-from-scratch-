from agent_framework import Agent,Tool
from urllib.parse import quote_plus
import json
import requests
from bs4 import BeautifulSoup

class webscraperTool(Tool):
    def __init__(self):
        super().__init__("scrape_website","scrapes contents from available website url")

    def execute(self,url:str)->dict:
        try:
            print(f"\nScraping:{url}")
            headers={'User-Agent':'Mozilla/5.0(Windows NT 10.0; Win64;x64)AppleWebKit/537.36'}
            response=requests.get(url,headers=headers,timeout=10)
            response.raise_for_status()

            soup=BeautifulSoup(response.content,'html.parser')
            for script in soup(["script","style"]):
                script.decompose()

            text=soup.get_text()
            lines=(line.strip() for line in text.splitlines())
            chunks=(phrase.strip() for line in lines for phrase in line.split(" "))
            text=''.join(chunk for chunk in chunks if chunk)
            text=text[:2000]
            print(f"Scrapped {len(text)} characters.")
            return {"url":url,"title":soup.title.string if soup.title else "No title","content":text,"status":"success"}
        
        except Exception as e:
            print(f"Error:{e}")
            return {"url":url,"error":str(e),"status":"failed"}
        
class GoogleSearchTool(Tool):
    def __init__(self):
        super().__init__("google_search","searches google and returns top results")

    def execute(self,query:str,num_results:int=5)->list:
        try:
            print(f"\n Searching Google for :{query}")
            url=(f" https://www.google.com/search?q={quote_plus(query)}")
            headers={'User-Agent':'Mozilla/5.0(Windows NT 10.0; Win64;x64)AppleWebKit/537.36'}
            response=requests.get(url,headers=headers,timeout=10)
            soup=BeautifulSoup(response.content,'html.parser')

            results=[]
            for g in soup.find_all('div',class_='g')[:num_results]:
                try:
                    title=g.find('h3').text if g.find('h3') else "No title"
                    link=g.find('a')['href']if g.find('a')else "No link"
                    snippet=g.find('div',class_='VwiC3b').text if g.find('div',class_='VwiC3b')else "No description"
                    results.append(
                        {
                            "title":title,
                            "link":link,
                            "snippet":snippet
                        }
                    )
                except:
                    continue
            print(f"Found {len(results)} results")
            return results
        except Exception as e:
            print(f"Error:{e}")
            return [{"error":str(e)}]
        
class wikipediaTool(Tool):
    def __init__(self):
        super().__init__("wikipedia","Gets information from wikipedia")

    def execute(self,topic:str)->dict:
        try:
            print(f"\n Fetching wikipedia :{topic}")
            url="https://en.wikipedia.org/api/rest_v1/page/summary/" + quote_plus(topic)
            response=requests.get(url,timeout=10)
            data=response.json()

            if 'title' not in data:
                return {"error":"Article not found"}
            result={
                "title":data.get('title'),
                "summary":data.get('extract'),
                "url":data.get('content_urls',{}).get('desktop',{}).get('page'),
                "status":"success"
            }
            print(f"Retrived :{result['title']}")
            return result
        except Exception as e:
            print(f"Error:{e}")
            return{"error":str(e)}
        
class NewsScrapperTool(Tool):
    def __init__(self):
        super().__init__("gets_news","Gets latest news headlines.")

    def execute(self,topic:str="technology")->list:
        try:
            print(f"\n Fetching news:{topic}")
            url=f"https://www.google.com/search?q={quote_plus(topic)}"
            headers={'User-Agent':'Mozilla/5.0(Windows NT 10.0; Win64;x64)AppleWebKit/537.36'}
            response=requests.get(url,headers=headers,timeout=10)
            soup=BeautifulSoup(response.content,'html.parser')

            articles=[]
            for article in soup.find_all('article')[:10]:
                try:
                    title_element=article.find('a')
                    if title_element:
                        articles.append({
                            "title":title_element.text,
                            "link":"https://news.google.com" + title_element['href'][1:]
                        })
                except :
                    continue
            print(f"Found {len(articles)}articles")
            return articles
        except Exception as e :
            print(F"Error:{e}")
            return[{"error":str(e)}]
        
class WeatherTool(Tool):
    def __init__(self):
        super().__init__("get_weather","Gets current weather for any city")

    def execute(self,city:str)->dict:
        try:
            print(f"Fetching weather:{city}")
            url=f"https://wttr.in/{quote_plus(city)}?format=j1"
            response=requests.get(url,timeout=10)
            data=response.json()
            current=data['current_condition'][0]

            result={
                "city":city,
                "temperature_c":current['temp_C'],
                "temperature_f":current['temp_F'],
                "condition":current['weatherDesc'][0]['value'],
                "humidity":current['humidity'],
                "wind_speed_Kmph":current['windspeedKmph'],
                "feels_like_c":current['FeelsLikeC'],
                "feels_like_f":current['FeelsLikeF']

            }
            print(f"{city}:{result['temperature_c']}c,{result['condition']}")
            return result
        except Exception as e:
            print(f"Error:{e}")
            return {"error":str(e),"city":city}

if __name__=="__main__":
    print("\n" + "="*60)
    print("WEB PULL AGENT")
    print("="*60)
    research_agent=Agent(
        name="RESEARCHAGENT",
        system_prompt="""You are a research assistant that helps users find information on the internet.
        Your Capabilities:
        -Scrape_website:Extract content from any URL
        -goole_search:Search Google for information
        -wikipedia:Get wikipedia articles
        -get_news:Get latest news headlines
        -get_weather:Get current weather for any city

        Important:When you need to use a tool,respond EXACTLY like this:
        USE_TOOL:tool_name
        PARAMS:param1=value1,param2=value2

        Examples:
        User asks:"What's the weather in Lagos?"
        Your response:
        USE_TOOL:get_weather
        PARAMS:city=Lagos
        User asks:"Tell me about Bitcoin"
        Your response:
        USE_TOOL:wikipedia
        PARAMS:topic=Bitcoin

        User asks:"Latest AI news"
        Your response:
        USE_TOOL:get_news
        PARAMS:topic=AI

        User asks:"Search for Python tutorials"
        Your response:
        USE_TOOL:google_search
        PARAMS:query=Python tutorials

        After the tool returns data,I will ask you to explain the results to the user in  natural language

        """,
        model="gpt-4o",
        require_approval=False
    )
    research_agent.register_tool(webscraperTool())
    research_agent.register_tool(GoogleSearchTool())
    research_agent.register_tool(wikipediaTool())
    research_agent.register_tool(NewsScrapperTool())
    research_agent.register_tool(WeatherTool())
    
    print("\n Research Agent is ready:")
    
    while True:
        try:
            
       
         user_input=input("You:").strip()
         if not user_input:
            continue
         if user_input.lower() in ['quit','exit','bye','q']:
            print("\n Research Agent shutting down")
            break
         elif user_input.lower()=='status':
            status=research_agent.get_status()
            print("\n Agent Status:")
            print(f" Name:{status['name']}")
            print(f"Conversations:{status['memory']['conversation_count']}")
            print(f"Tools:{','.join(status['tools'])}")
            print(f"Errors:{status['errors']['total_errors']}")
            print(f"Approvals:{status['approvals']}")
            print()
            continue
         elif user_input.lower()=="clear":
            research_agent.memory.clear_short_term()
            print("\n Conversation memory cleared!\n")
            continue
         elif user_input.lower().startswith('weather'):
            city=user_input[8:].strip()
            if city:
                result=research_agent.execute_tool("get_weather",city=city)
                if result.get("success"):
                    data=result.get("result")
                    print(f"\n Weather in {data.get('city')}")
                    print(f" Temperature:{data.get('temperature_c')}C({data.get("temperature_f")}F)")
                    print(f" Condition:{data.get('condition')}")
                    print(f" Humidity: {data.get('humidity')}")
                    print(f" Wind Speed:{data.get('wind_speed_kmph')}km/h")
                    print(f" Feels like :{data.get('feels_like_c')}C ({data.get('feels_like_f')}F)")
                else:
                    print(f"\n Error: {result.get('error')}")
                print()
            else:
                print("\n Please specify a city. Example:weather  London\n")
            continue
         elif user_input.lower().startswith("wiki"):
            topic=user_input[5:].strip()
            if topic:
                result=research_agent.execute_tool("wikipedia",topic=topic)
                if result.get("success"):
                    data=result.get("result")
                    if data.get("status")=="success":
                        print("\n Wikipedia:{data.get('title)}")
                        print(f"\n {data.get('summary')}")
                        print(f"\n Read more: {data.get('url')}")

                    else:
                        print(f"\n {data.get('error')}")

                else:
                    print(f"\n Error: {result.get('error')}")
                print()
            else:
                print("\n Please specify a topic.Example:wiki Bitcoin\n")
                continue
         elif user_input.lower().startswith('search'):
            query=user_input[7:].strip()
            if query:
                result=research_agent.execute_tool("google_search",query=query,num_results=5)
                if result.get("success"):
                    data=result.get("result")
                    print(f"\n Search Results for :{query}\n")
                    for i,item in enumerate(data,1):
                        if "error" in item:
                            print(f"Error:{item['error']}")
                        else:
                            print(f"{i}.{item.get('title')}")
                            print(f" {item.get('snippet')}")
                            print(f" {item.get('link')}")
                            print()
                else:
                    print(f"\n Error:{result.get('error')}\n")
            else:
                print("\n Please speify a search query.Example: search python tutorials\n")
            continue
         elif user_input.lower().startswith('news'):
            topic=user_input[5:].strip()
            if topic:
                result=research_agent.execute_tool("get_news",topic=topic)
                if result.get("success"):
                    data=result.get("result")
                    print(f"\n Latest News: {topic}\n")
                    for i,article in enumerate(data,1):
                        if "error" in article:
                            print(f"Error:{article['error']}")
                        else:
                            print(f"{i}. {article.get('title')}")
                            print(f" {article.get('link')}")
                            print()
                else:
                    print(f"\n Error:{result.get('error')}\n")
            else:
                print("\n Please specify a topic.Example:news technology\n")
            continue
         elif user_input.lower().startswith('scrape'):
            url=user_input[7:].strip()
            if url:
                if not url.startswith('http'):
                    url='https://' + url
                result=research_agent.execute_tool("scrape_website",url=url)
                if result.get("success"):
                    data=result.get("result")
                    if data.get("status")=="success":
                        print(f"\n Scraped: {data.get('url')}")
                        print(f" Title: {data.get('title')}")
                        print(f"\n Content Preview:")
                        print(data.get('content')[:500]+ "...")
                    else:
                        print(f"\n Error:{data.get('error')}")
                else:
                    print(f"\n Error:{result.get('error')}")
                print()
            else:
                print("\n Please specify a URL.Example: scrape example.com\n")
            continue
         else:
            response=research_agent.run(user_input)
            print(f"\n Assistant:{response}\n")
        except KeyboardInterrupt:
            print("\n\n Interrupted by user")
            break
        except Exception as e:
            print(f"\n Unexpected error:{e}")
            print("Please try again or type 'quit' to exit:\n")
            continue
        print("\n" + "="*60)
        print("Session summary")
        print("="*60)
        final_status=research_agent.get_status()
        print(f"\n Total queries processed :{final_status['memory']['conversation_count']}")
        print(f"Tools available:{','.join(final_status['tools'])}")

        if final_status['errors']['total_errors' ] > 0:
            print(f"\n Recent errors.")
            for error in final_status['errors']['recent_errors']:
                print(f" - {error['function']}: {error['error']}")
        print("\n Research Agent Shutdown complete.")
        print("=" *60)