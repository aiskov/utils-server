# Utils Server

## Usage

Convert web page to PDF:

    /pdf?url=<url>

Convert web page to IMG:

    /img?url=<url>

Add watermark to image:

    /watermark?[proportion=<proportion|1.5>&]text=<text>&url=<url>
    
Resize image:

    /resize?[x=<width|450>&][y=<height|450>&]url=<url>
    
## Know Issues

* Resize: Size selection doesn't work 
* Watermark: Proportion selection doesn't work
