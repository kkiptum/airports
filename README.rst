
Get Airport Satellite Images from Google Maps
=============================================


Points:

-  For Google Maps search we use the old
   `URL Scheme <https://moz.com/blog/everything-you-never-wanted-to-know-about-google-maps-parameters>`_.
-  List of Airports is from
   `EASYPNR <https://www.easypnr.com/blog/download-airport-iata-codes/>`_.
   Excel download not API. Unzip and rename the csv to data.csv.
   (This should change to use the zip file as is.)
-  Use `Chrome Webdriver <https://chromedriver.chromium.org/downloads>`_
   and `Google Chrome headless <https://developers.google.com/web/updates/2017/04/headless-chrome>`_.
   Firefox has issues with generating screenshots in windows.

TODO:

-  Testing.
-  Logging.
-  Config file. - also terminal switches.
-  better error handling - now I am kinda lazy.
-  Save output to json or something so that it is easier to upload.
-  Can it check for which browser the system has. Try to download the webdriver for it.
-  Use the EASYPNR download as zip.