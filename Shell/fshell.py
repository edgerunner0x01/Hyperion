from bs4 import BeautifulSoup
import validators
import logging
import sys
import os
import json
from json import * 
from typing import Any
from random import randint
from colorama import init, Fore, Back, Style
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'module_to_import')))
from zProbe.Lib.zProbe import *

# Initialize colorama 
init(autoreset=True)

# Configure logging
class Log:
    LOG_LEVELS = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }

    def __init__(self, log_method: str = "DEBUG", logger_name: str = "Shell"):
        self.logger = logging.getLogger(logger_name)
        self.configure_logging(log_method)

    def configure_logging(self, log_method: str):
        try:
            log_level = self.LOG_LEVELS.get(log_method, logging.DEBUG)
            logging.basicConfig(level=log_level,
                                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                handlers=[
                                    logging.FileHandler("Log/Log.log"),
                                    logging.StreamHandler()
                                ])
        except Exception as e:
            self.logger.error("Error setting up logging: %s", e)

class Shell:
    """A command-line interface shell for performing various extraction tasks on a target URL."""

    Commands = [str(i) for i in range(9)] + ["S", "M", "C", "99", "", "P", "X"]

    def __init__(self):
        """Initializes the Shell with default values and messages."""
        self.banners = [f"""{Fore.MAGENTA}
     .'(  )\\    /(    /`-.   )\\.---.     /`-.  .'(     .-./(   )\\  )
 ,') \\  ) \\ (_.' /  ,' _  \\ (   ,-._(  ,' _  \\ \\  )  ,'     ) (  \\, /  
(  '-' (   )  _.'  (  '-' (  \\  '-,   (  '-' ( ) (  (  .-, (   ) \\ (   
 ) .-.  )  / /      ) ,._.'   ) ,-`    ) ,_ .' \\  )  ) '._\\ ) ( ( \\ \\  
(  ,  ) \\ (  \\     (  '      (  ``-.  (  ' ) \\  ) \\ (  ,   (   `.)/  ) 
 )/    )/  ).'      )/        )..-.(   )/   )/   )/  )/ ._.'      '.(\n
            https://github.com/edgerunner0x01/Hyperion{Style.RESET_ALL}"""]

        self.help_message = f"""{Fore.MAGENTA}
Options:
  {Fore.LIGHTMAGENTA_EX}[1] Extract HTML Comments{Fore.RESET}
      Extracts all HTML comments from the target web page.
      HTML comments are sections enclosed within <!-- and -->.
      Useful for finding hidden notes or sections that may contain sensitive information.
      Example: <!-- This is a comment -->

  {Fore.LIGHTMAGENTA_EX}[2] Extract Meta Tags{Fore.RESET}
      Extracts metadata from the target web page.
      Includes tags like <meta name="description" content="...">.
      Useful for understanding the SEO setup and metadata used by the website.
      Example: <meta name="keywords" content="python, web, extraction">

  {Fore.LIGHTMAGENTA_EX}[3] Extract URLs (Links, Images, Scripts){Fore.RESET}
      Extracts all URLs from the target web page.
      Includes:
      - Hyperlinks (<a href="...">)
      - Image sources (<img src="...">)
      - Script sources (<script src="...">)
      Useful for gathering all linked resources on a page for analysis.
      Example: <a href="https://example.com">Link</a>

  {Fore.LIGHTMAGENTA_EX}[4] Extract Email Addresses{Fore.RESET}
      Extracts email addresses from the target web page.
      Searches for patterns that resemble email addresses (e.g., user@example.com).
      Useful for finding contact information.
      Example: user@example.com

  {Fore.LIGHTMAGENTA_EX}[5] Extract Robots.txt Content{Fore.RESET}
      Retrieves and displays the content of the robots.txt file from the target website.
      This file often contains rules for web crawlers about which parts of the site to avoid.
      Useful for understanding which parts of a site are restricted from crawling.
      Example: User-agent: *\nDisallow: /admin

  {Fore.LIGHTMAGENTA_EX}[6] Extract URLs from Sitemap.xml{Fore.RESET}
      Extracts all URLs listed in the sitemap.xml file from the target website.
      Sitemaps typically help search engines to better index a site.
      Useful for discovering all URLs the site owner wants to be indexed.
      Example: <url><loc>https://example.com/page1</loc></url>

  {Fore.LIGHTMAGENTA_EX}[7] Extract URLs from XML (Sitemap Schema){Fore.RESET}
      Parses any XML content conforming to the sitemap schema to extract URLs.
      Useful for custom sitemap formats or other structured XML data.
      Example: <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://example.com/page2</loc></url></urlset>

  {Fore.LIGHTMAGENTA_EX}[8] Extract WordPress Login Form Params{Fore.RESET}
      Extracts the form parameters required to log in to a WordPress site.
      This includes fields like username and password input names.
      Useful for identifying login forms and their parameters for automation.
      Example: <input type="text" name="log"> (username field)

  {Fore.LIGHTMAGENTA_EX}[S] Set Target (URL or File Path){Fore.RESET}
      Sets the target URL for subsequent extraction operations.
      You can also set a file path containing multiple URLs, one per line.
      Example: "S https://example.com" or "S urls.txt"

  {Fore.LIGHTMAGENTA_EX}[P] Set Proxies (JSON File Path){Fore.RESET}
      Sets the proxies from a JSON file for the extraction tasks.
      The JSON file should contain a list of proxies.
      Example: "P proxies.json"

  {Fore.LIGHTMAGENTA_EX}[X] Print Target HTML Source{Fore.RESET}
      Prints the entire HTML source of the target web page.
      Useful for a quick inspection of the HTML structure.
      Example: <html><head>...</head><body>...</body></html>

  {Fore.LIGHTMAGENTA_EX}[M] Menu{Fore.RESET}
      Displays the main menu with options to choose from.

  {Fore.LIGHTMAGENTA_EX}[C] Clear{Fore.RESET}
      Clears the screen.

  {Fore.LIGHTMAGENTA_EX}[0] Help{Fore.RESET}
      Displays this help text, providing details about each option and how to use them.

  {Fore.LIGHTMAGENTA_EX}[99] Exit{Fore.RESET}
      Exits the program.
{Style.RESET_ALL}

"""
  
        self.target = None
        self.targets = []
        self.proxies=[]
        self.proxies_path=None
        self.menu = f"""{Fore.MAGENTA}
# Select an option:

{Fore.LIGHTMAGENTA_EX}[1] Extract HTML Comments{Fore.RESET}
{Fore.LIGHTMAGENTA_EX}[2] Extract Meta Tags{Fore.RESET}
{Fore.LIGHTMAGENTA_EX}[3] Extract URLs (Links, Images, Scripts){Fore.RESET}
{Fore.LIGHTMAGENTA_EX}[4] Extract Email Addresses{Fore.RESET}
{Fore.LIGHTMAGENTA_EX}[5] Extract Robots.txt Content{Fore.RESET}
{Fore.LIGHTMAGENTA_EX}[6] Extract URLs from Sitemap.xml{Fore.RESET}
{Fore.LIGHTMAGENTA_EX}[7] Extract URLs from XML (Sitemap Schema){Fore.RESET}
{Fore.LIGHTMAGENTA_EX}[8] Extract WordPress Login Form Params{Fore.RESET}

{Fore.CYAN}[S] Set target (URL or File Path) [{self.target}]{Fore.RESET}
{Fore.CYAN}[P] Set Proxies (JSON File Path) [{None if self.proxies_path == [] else self.proxies_path}]{Fore.RESET}
{Fore.CYAN}[X] Print target HTML Source{Fore.RESET}
{Fore.CYAN}[M] Menu{Fore.RESET}
{Fore.CYAN}[C] Clear{Fore.RESET}
{Fore.CYAN}[0] Help{Fore.RESET}
{Fore.CYAN}[99] Exit{Fore.RESET}{Style.RESET_ALL}
"""
        self.prompt = f"{Fore.LIGHTMAGENTA_EX}Hyperion > {Style.RESET_ALL}"

    def Run(self):
        """Runs the shell, handling user input and directing to appropriate functions."""
        logging.info("Starting the shell.")
        while True:
            try:
                execute = input(self.prompt).strip().upper()
                if execute in Shell.Commands:
                    self.execute_command(execute)
                else:
                    print(f"{Fore.RED}Invalid option! Please try again.{Style.RESET_ALL}")
            except Exception as e:
                logging.error(f"An error occurred: {e}")
                print(f"{Fore.RED}An unexpected error occurred: {e}{Style.RESET_ALL}")

    def execute_command(self, command):
        """Executes the command based on user input."""
        if command == "X":
            self.extract_source()
        elif command == "1":
            self.extract_html_comments()
        elif command == "2":
            self.extract_meta_tags()
        elif command == "3":
            self.extract_urls()
        elif command == "4":
            self.extract_email_addresses()
        elif command == "5":
            self.extract_robots_txt()
        elif command == "6":
            self.extract_urls_from_sitemap()
        elif command == "7":
            self.extract_urls_from_xml()
        elif command == "8":
            self.extract_wp_login_form_params()
        elif command == "S":
            self.set_target()
        elif command == "P":
            self.set_proxies()
        elif command == "C":
            self.Clear()
        elif command == "M":
            self.Menu()
        elif command == "0":
            self.Help()
        elif command == "99":
            self.exit_shell()

    def set_target(self):
        """Sets the target URL or multiple target URLs for extraction."""
        try:
            choice = input(f"{Fore.CYAN}[*] Set Target (URL or file path): {Style.RESET_ALL}").strip()
            
            # Check if the input is a valid URL
            if validators.url(choice):
                self.target = choice
                print(f"{Fore.GREEN}[+] Target is set to '{self.target}' successfully.{Style.RESET_ALL}")
                self.menu = f"""{Fore.MAGENTA}
# Select an option:

{Fore.LIGHTMAGENTA_EX}[1] Extract HTML Comments{Fore.RESET}
{Fore.LIGHTMAGENTA_EX}[2] Extract Meta Tags{Fore.RESET}
{Fore.LIGHTMAGENTA_EX}[3] Extract URLs (Links, Images, Scripts){Fore.RESET}
{Fore.LIGHTMAGENTA_EX}[4] Extract Email Addresses{Fore.RESET}
{Fore.LIGHTMAGENTA_EX}[5] Extract Robots.txt Content{Fore.RESET}
{Fore.LIGHTMAGENTA_EX}[6] Extract URLs from Sitemap.xml{Fore.RESET}
{Fore.LIGHTMAGENTA_EX}[7] Extract URLs from XML (Sitemap Schema){Fore.RESET}
{Fore.LIGHTMAGENTA_EX}[8] Extract WordPress Login Form Params{Fore.RESET}

{Fore.CYAN}[S] Set target (URL or File Path) [{self.target}]{Fore.RESET}
{Fore.CYAN}[P] Set Proxies (JSON File Path) [{None if self.proxies_path == [] else self.proxies_path}]{Fore.RESET}
{Fore.CYAN}[X] Print target HTML Source{Fore.RESET}
{Fore.CYAN}[M] Menu{Fore.RESET}
{Fore.CYAN}[C] Clear{Fore.RESET}
{Fore.CYAN}[0] Help{Fore.RESET}
{Fore.CYAN}[99] Exit{Fore.RESET}{Style.RESET_ALL}
"""
                logging.info(f"Target set to: {self.target}")
            
            # Check if the input is a file path
            elif os.path.isfile(choice):
                with open(choice, 'r') as file:
                    urls = file.readlines()
                    urls = [url.strip() for url in urls if validators.url(url.strip())]
                    if urls:
                        self.targets = urls  # Store all valid URLs from the file
                        print(f"{Fore.GREEN}[+] Targets are set from file: '{choice}'{Style.RESET_ALL}")
                        self.menu = f"""{Fore.MAGENTA}
# Select an option:

{Fore.LIGHTMAGENTA_EX}[1] Extract HTML Comments{Fore.RESET}
{Fore.LIGHTMAGENTA_EX}[2] Extract Meta Tags{Fore.RESET}
{Fore.LIGHTMAGENTA_EX}[3] Extract URLs (Links, Images, Scripts){Fore.RESET}
{Fore.LIGHTMAGENTA_EX}[4] Extract Email Addresses{Fore.RESET}
{Fore.LIGHTMAGENTA_EX}[5] Extract Robots.txt Content{Fore.RESET}
{Fore.LIGHTMAGENTA_EX}[6] Extract URLs from Sitemap.xml{Fore.RESET}
{Fore.LIGHTMAGENTA_EX}[7] Extract URLs from XML (Sitemap Schema){Fore.RESET}
{Fore.LIGHTMAGENTA_EX}[8] Extract WordPress Login Form Params{Fore.RESET}

{Fore.CYAN}[S] Set target (URL or File Path) [{choice}]{Fore.RESET}
{Fore.CYAN}[P] Set Proxies (JSON File Path) [{None if self.proxies_path == [] else self.proxies_path}]{Fore.RESET}
{Fore.CYAN}[X] Print target HTML Source{Fore.RESET}
{Fore.CYAN}[M] Menu{Fore.RESET}
{Fore.CYAN}[C] Clear{Fore.RESET}
{Fore.CYAN}[0] Help{Fore.RESET}
{Fore.CYAN}[99] Exit{Fore.RESET}{Style.RESET_ALL}
"""
                        logging.info(f"Targets set from file: {choice}")
                    else:
                        print(f"{Fore.RED}[!] No valid URLs found in the file. Please check the file content.{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}[!] Invalid URL or file path. Please try again.{Style.RESET_ALL}")
        
        except Exception as e:
            logging.error(f"Failed to set target: {e}")
            print(f"{Fore.RED}An error occurred while setting the target: {e}{Style.RESET_ALL}")

    def Menu(self):
        """Displays the menu options."""
        print(self.menu)

    def Help(self):
        """Displays the help message."""
        print(self.help_message)

    def Banner(self):
        print(self.banners[randint(0, len(self.banners) - 1)])

    def exit_shell(self):
        logging.info("Exiting the shell.")
        print(f"{Fore.GREEN}Exiting the program.{Style.RESET_ALL}")
        exit()

######################################################################################################################################################
    def get_user_input(self):
        """
        Prompts the user for the filename and file format, ensuring they are valid.
        
        :return: Tuple containing the filename and file format.
        """
        while True:
            filename = input(f"{Fore.CYAN}Enter the filename (with extension): {Style.RESET_ALL}").strip()
            if not filename:
                print(f"{Fore.RED}Filename cannot be empty. Please try again.{Style.RESET_ALL}")
                continue
            if not os.path.splitext(filename)[1]:
                print(f"{Fore.RED}Filename must include an extension (e.g., .txt, .json). Please try again.{Style.RESET_ALL}")
                continue
            break

        while True:
            file_format = input(f"{Fore.CYAN}Enter the file format (text, json, binary): {Style.RESET_ALL}").strip().lower()
            if file_format not in ['text', 'json', 'binary']:
                print(f"{Fore.RED}Invalid file format. Please enter 'text', 'json', or 'binary'.{Style.RESET_ALL}")
                continue
            break

        return filename, file_format

    def write_to_file(self,filename: str, data: Any,  file_format: str = 'text') -> bool:
        """
        Writes data to a file with specified format and mode.

        :param filename: Name of the file to write to.
        :param data: Data to be written to the file.
        :param mode: Mode in which to open the file ('w' for writing, 'a' for appending, etc.).
        :param file_format: Format of the file ('text', 'json', 'binary').
        :return: True if the writing is successful, False otherwise.
        """
        mode :str="a+"
        try:
            if file_format == 'text':
                with open(filename, mode, encoding='utf-8') as file:
                    for i in data:
                        file.write(str(i).rstrip()+"\n")
            elif file_format == 'json':
                with open(filename, mode, encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=4)
            elif file_format == 'binary':
                with open(filename, mode + 'b') as file:
                    file.write(data)
            else:
                raise ValueError(f"{Fore.RED}Unsupported file format specified.{Style.RESET_ALL}")

            logging.info(f"Data successfully written to {filename}")
            return True

        except Exception as e:
            logging.error(f"Failed to write to {filename}: {e}")
            return False
        
    def save(self):
        """
        Prompts the user if they want to save the data to a file.
        
        :param data: Data to be stored in the file.
        """
        save_response = input(f"{Fore.CYAN}Do you want to save the output to a file? (yes/no): {Style.RESET_ALL}").strip().lower()
        if save_response in ['yes', 'y']:
            return True
        else:
            return False
######################################################################################################################################################
    def Clear(self):
        try:
            os.system('cls' if os.name == 'nt' else 'clear')
        except Exception as e:
            logging.error(f"Exception occurred while clearing the screen: {e}")

    def load_proxies(self, proxies_file):
        """Loads proxies from a JSON file."""
        try:
            choice=proxies_file
            self.proxies_path=choice
            with open(proxies_file, 'r') as f:
                proxies_data = json.load(f)
                print(f"{Fore.GREEN}[+] Proxies are set to '{choice}' successfully.{Style.RESET_ALL}")
                self.menu = f"""{Fore.MAGENTA}
# Select an option:

{Fore.LIGHTMAGENTA_EX}[1] Extract HTML Comments{Fore.RESET}
{Fore.LIGHTMAGENTA_EX}[2] Extract Meta Tags{Fore.RESET}
{Fore.LIGHTMAGENTA_EX}[3] Extract URLs (Links, Images, Scripts){Fore.RESET}
{Fore.LIGHTMAGENTA_EX}[4] Extract Email Addresses{Fore.RESET}
{Fore.LIGHTMAGENTA_EX}[5] Extract Robots.txt Content{Fore.RESET}
{Fore.LIGHTMAGENTA_EX}[6] Extract URLs from Sitemap.xml{Fore.RESET}
{Fore.LIGHTMAGENTA_EX}[7] Extract URLs from XML (Sitemap Schema){Fore.RESET}
{Fore.LIGHTMAGENTA_EX}[8] Extract WordPress Login Form Params{Fore.RESET}

{Fore.CYAN}[S] Set target (URL or File Path) [{self.target}]{Fore.RESET}
{Fore.CYAN}[P] Set Proxies (JSON File Path) [{choice}]{Fore.RESET}
{Fore.CYAN}[X] Print target HTML Source{Fore.RESET}
{Fore.CYAN}[M] Menu{Fore.RESET}
{Fore.CYAN}[C] Clear{Fore.RESET}
{Fore.CYAN}[0] Help{Fore.RESET}
{Fore.CYAN}[99] Exit{Fore.RESET}{Style.RESET_ALL}
"""
            logging.info(f"Proxies set from file: {choice}")
            return proxies_data
        except FileNotFoundError:
            logging.error(f"Error: Proxies file '{proxies_file}' not found.")
            print(f"{Fore.RED}Error: Proxies file '{proxies_file}' not found.{Fore.RESET}")
        except json.JSONDecodeError:
            logging.error(f"Error: Invalid JSON format in proxies file '{proxies_file}'.")
            print(f"{Fore.RED}Error: Invalid JSON format in proxies file '{proxies_file}'.{Fore.RESET}")
        return None
    
    def set_proxies(self):
        """Sets the Proxies list from a JSON file"""
        try:
            choice = input(f"{Fore.CYAN}[*] Set Proxies JSON File: {Style.RESET_ALL}").strip()            
        # Check if the input is a valid 
            self.proxies = self.load_proxies(choice) if choice else print(f"{Fore.RED}[!] Invalid URL or file path. Please try again.{Style.RESET_ALL}")
    
        except Exception as e:
            logging.error(f"Failed to set Proxies: {e}")
            print(f"{Fore.RED}An error occurred while setting the Proxies: {e}{Style.RESET_ALL}")

    #################################################
    # Methods to integrate with Target class methods#
    #################################################
    
    def ensure_target_set(self):
        if not self.target and not self.targets:
            print(f"{Fore.RED}Target URL(s) is not set. Use 'S' command to set the target(s).{Style.RESET_ALL}")
            logging.warning("Target(s) URL is not set.")
            return False
        elif self.target and not validators.url(self.target):
            print(f"{Fore.RED}Invalid URL set as target. Please set a valid URL using 'S'.{Style.RESET_ALL}")
            logging.warning("Invalid URL set as target.")
            return False
        return True

    def extract_html_comments(self):
        choice = self.save()
        if choice:
            filename, file_format = self.get_user_input()
        if self.ensure_target_set():
            try:
                if isinstance(self.targets, list) and len(self.targets) > 0:  # Check if multiple targets are set
                    for target_url in self.targets:
                        target = Target(target_url,self.proxies)
                        comments, success = target.Extract_Comments()
                        if success:
                            logging.info(f"Extracted HTML comments from {target_url} successfully.")
                            print(f"{Fore.GREEN}{comments}{Style.RESET_ALL}")
                            if choice:
                                self.write_to_file(filename, comments, file_format)

                        else:
                            logging.error(f"Failed to extract HTML comments from {target_url}: {comments}")
                            print(f"{Fore.RED}Error extracting HTML comments from {target_url}: {comments}{Style.RESET_ALL}")
                else:
                    target = Target(self.target)
                    comments, success = target.Extract_Comments()
                    if success:
                        logging.info("Extracted HTML comments successfully.")
                        print(f"{Fore.GREEN}{comments}{Style.RESET_ALL}")
                        if choice:
                            self.write_to_file(filename, comments, file_format)

                    else:
                        logging.error(f"Failed to extract HTML comments: {comments}")
                        print(f"{Fore.RED}Error extracting HTML comments: {comments}{Style.RESET_ALL}")
            except Exception as e:
                logging.error(f"Exception occurred while extracting HTML comments: {e}")
                print(f"{Fore.RED}Exception occurred: {e}{Style.RESET_ALL}")

    def extract_meta_tags(self):
        choice =self.save()
        if choice:
            filename, file_format = self.get_user_input()
        if self.ensure_target_set():
            try:
                if isinstance(self.targets, list) and len(self.targets) > 0:  # Check if multiple targets are set
                    for target_url in self.targets:
                        target = Target(target_url,self.proxies)
                        metadata, success = target.Extract_MetaData()
                        if success:
                            logging.info(f"Extracted meta tags from {target_url} successfully.")
                            print(f"{Fore.GREEN}{metadata}{Style.RESET_ALL}")
                            if choice:
                                self.write_to_file(filename, metadata, file_format)
                        else:
                            logging.error(f"Failed to extract meta tags from {target_url}: {metadata}")
                            print(f"{Fore.RED}Error extracting meta tags from {target_url}: {metadata}{Style.RESET_ALL}")
                else:
                    target = Target(self.target)
                    metadata, success = target.Extract_MetaData()
                    if success:
                        logging.info("Extracted meta tags successfully.")
                        print(f"{Fore.GREEN}{metadata}{Style.RESET_ALL}")
                        if choice:
                            self.write_to_file(filename, metadata, file_format)
                    else:
                        logging.error(f"Failed to extract meta tags: {metadata}")
                        print(f"{Fore.RED}Error extracting meta tags: {metadata}{Style.RESET_ALL}")
            except Exception as e:
                logging.error(f"Exception occurred while extracting meta tags: {e}")
                print(f"{Fore.RED}Exception occurred: {e}{Style.RESET_ALL}")

    def extract_source(self):
        choice = self.save()
        if choice:
            filename, file_format = self.get_user_input()
            print(filename)
        if self.ensure_target_set():
            try:
                if isinstance(self.targets, list) and len(self.targets) > 0:  # Check if multiple targets are set
                    for target_url in self.targets:
                        target = Target(target_url,self.proxies)
                        if target.HTTP_STATUS == 200:
                            source = BeautifulSoup(target.source, 'html.parser').prettify()
                            logging.info(f"Extracted HTML Source from {target_url} successfully.")
                            print(f"{Fore.GREEN}{source}{Style.RESET_ALL}")
                            
                            if choice:
                                self.write_to_file(filename, source, file_format)

                        else:
                            logging.error(f"Failed to extract HTML Source from {target_url}: HTTP Status {target.HTTP_STATUS}")
                            print(f"{Fore.RED}Error extracting HTML Source from {target_url}: HTTP Status {target.HTTP_STATUS}{Style.RESET_ALL}")
                else:
                    target = Target(self.target)
                    if target.HTTP_STATUS == 200:
                        source = BeautifulSoup(target.source, 'html.parser').prettify()
                        logging.info("Extracted HTML Source successfully.")
                        print(f"{Fore.GREEN}{source}{Style.RESET_ALL}")
                        if choice:
                            self.write_to_file(filename, source, file_format)

                    else:
                        logging.error(f"Failed to extract HTML Source: HTTP Status {target.HTTP_STATUS}")
                        print(f"{Fore.RED}Error extracting HTML Source: HTTP Status {target.HTTP_STATUS}{Style.RESET_ALL}")
            except Exception as e:
                logging.error(f"Exception occurred while extracting HTML Source: {e}")
                print(f"{Fore.RED}Exception occurred: {e}{Style.RESET_ALL}")

    def extract_urls(self):
        choice = self.save()
        if choice :
            filename, file_format = self.get_user_input()
        if self.ensure_target_set():
            try:
                if isinstance(self.targets, list) and len(self.targets) > 0:  # Check if multiple targets are set
                    for target_url in self.targets:
                        target = Target(target_url,self.proxies)
                        urls, success = target.Extract_URLS()
                        if success:
                            logging.info(f"Extracted URLs from {target_url} successfully.")
                            print(f"{Fore.GREEN}{urls}{Style.RESET_ALL}")
                            if choice:
                                self.write_to_file(filename, urls, file_format)
                        else:
                            logging.error(f"Failed to extract URLs from {target_url}: {urls}")
                            print(f"{Fore.RED}Error extracting URLs from {target_url}: {urls}{Style.RESET_ALL}")
                else:
                    target = Target(self.target)
                    urls, success = target.Extract_URLS()
                    if success:
                        logging.info("Extracted URLs successfully.")
                        print(f"{Fore.GREEN}{urls}{Style.RESET_ALL}")
                        if choice:
                            self.write_to_file(filename, urls, file_format)
                    else:
                        logging.error(f"Failed to extract URLs: {urls}")
                        print(f"{Fore.RED}Error extracting URLs: {urls}{Style.RESET_ALL}")
            except Exception as e:
                logging.error(f"Exception occurred while extracting URLs: {e}")
                print(f"{Fore.RED}Exception occurred: {e}{Style.RESET_ALL}")

    def extract_email_addresses(self):
        choice = self.save()
        if choice :
            filename, file_format = self.get_user_input()
        if self.ensure_target_set():
            try:
                if isinstance(self.targets, list) and len(self.targets) > 0:  # Check if multiple targets are set
                    for target_url in self.targets:
                        target = Target(target_url,self.proxies)
                        emails, success = target.Extract_Emails()
                        if success:
                            logging.info(f"Extracted email addresses from {target_url} successfully.")
                            print(f"{Fore.GREEN}{emails}{Style.RESET_ALL}")
                            if choice:
                                self.write_to_file(filename, emails, file_format)
                        else:
                            logging.error(f"Failed to extract email addresses from {target_url}: {emails}")
                            print(f"{Fore.RED}Error extracting email addresses from {target_url}: {emails}{Style.RESET_ALL}")
                else:
                    target = Target(self.target)
                    emails, success = target.Extract_Emails()
                    if success:
                        logging.info("Extracted email addresses successfully.")
                        print(f"{Fore.GREEN}{emails}{Style.RESET_ALL}")
                        if choice:
                            self.write_to_file(filename, emails, file_format)
                    else:
                        logging.error(f"Failed to extract email addresses: {emails}")
                        print(f"{Fore.RED}Error extracting email addresses: {emails}{Style.RESET_ALL}")
            except Exception as e:
                logging.error(f"Exception occurred while extracting email addresses: {e}")
                print(f"{Fore.RED}Exception occurred: {e}{Style.RESET_ALL}")

    def extract_robots_txt(self):
        choice = self.save()
        if choice:
            filename, file_format = self.get_user_input()
        if self.ensure_target_set():
            try:
                if isinstance(self.targets, list) and len(self.targets) > 0:  # Check if multiple targets are set
                    for target_url in self.targets:
                        target = Target(target_url,self.proxies)
                        content, status_code, success = target.Extract_Robots()
                        if success:
                            logging.info(f"Extracted robots.txt content from {target_url} successfully.")
                            print(f"{Fore.GREEN}{content}{Style.RESET_ALL}")
                            if choice:
                                self.write_to_file(filename, content, file_format)
                        else:
                            logging.error(f"Failed to extract robots.txt content from {target_url}: {content}")
                            print(f"{Fore.RED}Error extracting robots.txt content from {target_url}: {content}{Style.RESET_ALL}")
                else:
                    target = Target(self.target)
                    content, status_code, success = target.Extract_Robots()
                    if success:
                        logging.info("Extracted robots.txt content successfully.")
                        print(f"{Fore.GREEN}{content}{Style.RESET_ALL}")
                        if choice:
                            self.write_to_file(filename, content, file_format)
                    else:
                        logging.error(f"Failed to extract robots.txt content: {content}")
                        print(f"{Fore.RED}Error extracting robots.txt content: {content}{Style.RESET_ALL}")
            except Exception as e:
                logging.error(f"Exception occurred while extracting robots.txt content: {e}")
                print(f"{Fore.RED}Exception occurred: {e}{Style.RESET_ALL}")

    def extract_urls_from_sitemap(self):
        choice = self.save()
        if choice:
            filename, file_format = self.get_user_input()
        if self.ensure_target_set():
            try:
                if isinstance(self.targets, list) and len(self.targets) > 0:  # Check if multiple targets are set
                    for target_url in self.targets:
                        target = Target(target_url,self.proxies)
                        urls, status_code, success = target.Extract_Sitemap()
                        if success:
                            logging.info(f"Extracted URLs from sitemap.xml at {target_url} successfully.")
                            print(f"{Fore.GREEN}{urls}{Style.RESET_ALL}")
                            if choice:
                                self.write_to_file(filename, urls, file_format)
                        else:
                            logging.error(f"Failed to extract URLs from sitemap.xml at {target_url}: {urls}")
                            print(f"{Fore.RED}Error extracting URLs from sitemap.xml at {target_url}: {urls}{Style.RESET_ALL}")
                else:
                    target = Target(self.target)
                    urls, status_code, success = target.Extract_Sitemap()
                    if success:
                        logging.info("Extracted URLs from sitemap.xml successfully.")
                        print(f"{Fore.GREEN}{urls}{Style.RESET_ALL}")
                        if choice:
                            self.write_to_file(filename, urls, file_format)
                    else:
                        logging.error(f"Failed to extract URLs from sitemap.xml: {urls}")
                        print(f"{Fore.RED}Error extracting URLs from sitemap.xml: {urls}{Style.RESET_ALL}")
            except Exception as e:
                logging.error(f"Exception occurred while extracting URLs from sitemap.xml: {e}")
                print(f"{Fore.RED}Exception occurred: {e}{Style.RESET_ALL}")

    def extract_urls_from_xml(self):
        choice = self.save()
        if choice:
            filename, file_format = self.get_user_input()
        if self.ensure_target_set():
            try:
                if isinstance(self.targets, list) and len(self.targets) > 0:  # Check if multiple targets are set
                    for target_url in self.targets:
                        target = Target(target_url,self.proxies)
                        urls, status_code, success = target.Extract_XML_URLS()
                        if success:
                            logging.info(f"Extracted URLs from XML content at {target_url} successfully.")
                            print(f"{Fore.GREEN}{urls}{Style.RESET_ALL}")
                            if choice:
                                self.write_to_file(filename, urls, file_format)
                        else:
                            logging.error(f"Failed to extract URLs from XML content at {target_url}: {urls}")
                            print(f"{Fore.RED}Error extracting URLs from XML content at {target_url}: {urls}{Style.RESET_ALL}")
                else:
                    target = Target(self.target)
                    urls, status_code, success = target.Extract_XML_URLS()
                    if success:
                        logging.info("Extracted URLs from XML content successfully.")
                        print(f"{Fore.GREEN}{urls}{Style.RESET_ALL}")
                        if choice:
                            self.write_to_file(filename, urls, file_format)
                    else:
                        logging.error(f"Failed to extract URLs from XML content: {urls}")
                        print(f"{Fore.RED}Error extracting URLs from XML content: {urls}{Style.RESET_ALL}")
            except Exception as e:
                logging.error(f"Exception occurred while extracting URLs from XML content: {e}")
                print(f"{Fore.RED}Exception occurred: {e}{Style.RESET_ALL}")

    def extract_wp_login_form_params(self):
        choice = self.save()
        if choice :
            filename, file_format = self.get_user_input()
        if self.ensure_target_set():
            try:
                if isinstance(self.targets, list) and len(self.targets) > 0:  # Check if multiple targets are set
                    for target_url in self.targets:
                        target = Target(target_url,self.proxies)
                        form_params, status_code, success = target.Extract_WPLOGIN()
                        if success:
                            logging.info(f"Extracted WordPress login form parameters from {target_url} successfully.")
                            print(f"{Fore.GREEN}{form_params}{Style.RESET_ALL}")
                            if choice:
                                self.write_to_file(filename, form_params, file_format)
                        else:
                            logging.error(f"Failed to extract WordPress login form parameters from {target_url}: {form_params}")
                            print(f"{Fore.RED}Error extracting WordPress login form parameters from {target_url}: {form_params}{Style.RESET_ALL}")
                else:
                    target = Target(self.target)
                    form_params, status_code, success = target.Extract_WPLOGIN()
                    if success:
                        logging.info("Extracted WordPress login form parameters successfully.")
                        print(f"{Fore.GREEN}{form_params}{Style.RESET_ALL}")
                        if choice:
                            self.write_to_file(filename, form_params, file_format)
                    else:
                        logging.error(f"Failed to extract WordPress login form parameters: {form_params}")
                        print(f"{Fore.RED}Error extracting WordPress login form parameters: {form_params}{Style.RESET_ALL}")
            except Exception as e:
                logging.error(f"Exception occurred while extracting WordPress login form parameters: {e}")
                print(f"{Fore.RED}Exception occurred: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    shell = Shell()
    shell.Menu()
    shell.Run()