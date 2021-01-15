# GT-WebApp-Prototype

This repo contains the code and the files for running the query sharing web application. The repository has two branches: **master** and **dlab_server_v**. **dlab_server_v** is the branch containing the version of the website that is deployed to our server: http://51.158.119.80/. **master**, on the other hand, is the branch containing the code used for generating the local applications (executable files). The local apps are available [here](https://www.dropbox.com/sh/d9xx4hhoxvgw45t/AACG5BXsMzooYKOiYAHCHYmKa?dl=0). 

For installing the necessary python libraries you can just run ```pip install -r requirements.txt```.

#### File descriptions

*main.py* - the pyhton code running the web app.

*assets/* - this folder most importantly contains *header.css* which defines the design of the website. In addition, it contains the favicon and a couple png files used in the web app.

*sample.json* - this is a sample json file used for testing the functionality of the website.

#### How to generate the local apps?

1. ```pip install pyinstaller```
2. ```pyinstaller --onefile main.py```
3. A file named *main.spec* will be generated. Edit the file by adding the following:

**datas**=[('assets/header.css', 'assets'),
('assets/submission_successful.png', 'assets'),
('assets/smth_went_wrong.png', 'assets'),
('assets/tooltip.png', 'assets'),
('assets/favicon.ico','assets'),
('PATH_TO_YOUR_DASH_CORE_COMPONENTS_PACKAGE','dash_core_components'),
('PATH_TO_YOUR_DASH_HTML_COMPONENTS_PACKAGE','dash_html_components'),
('PATH_TO_YOUR_DASH_RENDERER_PACKAGE','dash_renderer'),
('PATH_TO_YOUR_DASH_BOOTSTRAP_COMPONENTS_PACKAGE','dash_bootstrap_components')],
**hiddenimports**=['_cffi_backend']

4. ```pyinstaller main.spec```
5. Access the standalone executable file in the folder *dist/*.

