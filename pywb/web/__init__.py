from enum import Enum

from pywb.web.chrome import Chrome

By = Enum("By",
          {"BUTTON": "//button|span[contains(text(), '%s')]",
           "LINK": "//a[contains(text(), '%s')]",
           "TEXT": "//*[not(self::a) and not(self::button) and contains(text(),'%s')]"})

BrowserType = Enum("BrowserType", {
    "CHROME": Chrome
})
