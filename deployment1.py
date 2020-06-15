import json
import os
import argparse
import logging
import getpass


logging.basicConfig(format='%(levelname)-8s %(message)s', level=logging.INFO)


class app_deployment:
    """
       Title : Deployment of multiple apps on Jetson device 
    """
    def __init__(self, username, path, ip, device, remote_user, apps):
        """
           Constructor To Define Global Objects
        """
        self.ip = ip
        self.username = getpass.getuser()
        self.path = path
        self.device = device
        self.remote_user = remote_user
        self.apps = apps

    def deploy(self):
        """
           Method to deploy multiple apps
           Output : Command of app deployment will be executed
        """
        """
           'data.json' is json file containing app name & its path
            This file is present in isaac folder
        """
        arg_flag = 0
        login_flag = 0
        if (type(self.ip)!= str or type(self.apps) != str or type(self.device) != str or type(self.remote_user) != str ):
            arg_flag = 1

        if (arg_flag == 0):
            arg_flag = 0
        else:
            raise Exception("Some of the Arguments missing...\n Required Args:1)IP of device(--ip) 2)Name of apps(--apps) 3)Name of Device\n Provide path of Isaac if it is not default")
        logging.info("Current Working Directory : %s", os.getcwd())
        isaac_path = ""
        ListOfFolder = []
        files = os.listdir()
        path = ""
        container = []
        apps = self.apps.split(',')
        for name in apps:
            
            #move to Isaac folder to execute the commands
            path_exist = os.chdir("/home/" + self.username + "/isaac")

            if(path_exist == None):
    
                try:
                    app_info = open('data.json','r')
                    data = json.load(app_info) 
                   
                    #search for the app name which we want to deploy
                    #Get path of app from json file
                    for info in data['app']:
                        if info['name'] == name :
                            path = info['path']
                            container.append(path)

                    if(len(path) < 1):
                        logging.error("App name Not-Found...try another App")  
                    else:
                        command = self.create_command(path)
                    
                    if(type(command) == str):
                        #try to execute the command
                        os.system(command)
                        
                    else:
                        logging.error("Could Not Deploy the App")

                except OSError:
                    logging.error("Json file Not-Found")


            #if path of Isaac folder is not default going to specified path
            else:
                checker =os.chdir(self.path + "/isaac")
                if(checker == "None"):
                    #move to path specified for Isaac folder
                    
                    logging.info("Working Directory changed to : %s", os.getcwd())
                    
                    try:
   
                        with open('data.json') as json_file:
                            data = json.load(json_file)

                        logging.info("Working Directory changed to : %s", os.getcwd())


                        #search for the app name which we want to deploy
                        #Get path of app from json file
                        for info in data['app']:
                            if info['name'] == name :
                                path = info['path']
                                container.append(path)


                        if(len(path) < 1):
                            logging.error("App name Not-Found...try another App")

                        else:
                            command = self.create_command(path)
                       
                        if (type(command) == str):
                            #execute the command
                            os.system(command)
                            
                        else:
                            logging.error("Could Not Deploy the App")

                    except OSError:
                        logging.error("Json file Not-Found")

                else:
                    logging.error("Could-not find Isaac Folder")


    def create_command(self,path):

        #Build Command to Deploy the app
        command = "./engine/build/deploy.sh --remote_user " + self.remote_user + " -d " + self.device + " -p " + path +  "  -h " + self.ip
        logging.info("Command to Execute : %s", command)
        return command

    def run_application(self):
        """
           This method does following ways:
           login to Robot => Move to deploy folder => Go to each folder & run program 
        """

        #login to robot 
        login_command = "ssh " + self.remote_user + "@" + self.ip
        logging.info("Logging to Robot")
        login_checker = os.system(login_command)
        i = 0
        
        if(login_checker == "None"):
            try:
                #move to deploy folder
                os.chdir("deploy/" + self.username)
                for package in os.listdir(os.getcwd()):
                    if os.path.isdir(package):
                        os.chdir(package)
                        path = container[i]
                        path = path.replace(":","/") 
                        path = path[1:]
                        path = path[:-3]
                        run_command = "." + path
                        os.system(run_command)
                        i += 1
            except:
                logging.info("Folder does not exist")
        else:
            logging.error("Could-not login to Robot")

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--isaac_path", help="Enter path Of Isaac folder")
    parser.add_argument("--username", help="Enter Username Of System")
    parser.add_argument("--ip", help = "IP of device")
    parser.add_argument("--device", help = "Name of Jetson device")
    parser.add_argument("--remote_user", help = "Name of Remote user")
    parser.add_argument("--apps", help = "Name of Apps")
    args = parser.parse_args()
    #Setting default Username
    args.remote_user = "ubuntu"
    obj = app_deployment(args.username,args.isaac_path,args.ip,args.device,args.remote_user,args.apps)
    obj.deploy()
    obj.run_application()
    del obj
