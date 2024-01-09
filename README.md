# GPT Document Extraction

This is a proof-of-concept for using ChatGPT to extract structured data scanned images.

It works in 3 processes that could be split out. Each uses files in a directory as a queue, and ends by moving the file(s) to a different directory. 

1. Unzip
2. Call OCR API (currently AWS Textract)
3.  Call ChatGPT to determine the category of the OCR'd text (JSON output) a JSON record that matches a given JSON Schema specification. Then call ChatGPT to extract industry-specific fields from the OCR'd text (JSON output)

The 3 processes are run sequentially, 1, then 2, then 3.  These could be separate processes running in parallel. The whole sequence of processes is run by calling:

```
./gpt-extract.py 
```

The directory structure and function is:

```
> ls
- images
- images_done
- ocr
- ocr_done
- json_result
- schemas
```
#### images 
Images (jpg, png) or .zip files full of images are placed in the images directory.  If zipped, the first process will unzip the images, leaving them in the images directory.

#### images_done
Once the OCR service has successfully produced a text output file for an image, the image is moved to the image_done directory.

#### ocr
For each image, the AWS OCR service is called, writing the text output to a file with the same name without the _1 or _2 at the end.  Files with the sme

```
[{
  "id": 1
  "doc": "My text here..."
}, {
  "id": 2,
  "doc": "Another record..."
}]
```

You can run the script like this:

```
./gpt-extract.py --input-type json --keydoc doc --keyid id infile.json schema.json output.json
```

Note that the output file (`output.json`), if it exists, needs to be valid JSON (not a blank file) as the script will attempt to load it and continue where the extraction left off.

## Setup

Cloning will set up 6 directories
```
git clone  git@github.com:pauljmillar/chatgpt_doc_parser.git
cd chatgpt-document-extraction
pip install .
```

### Input data spec

You can provide one of two options:

1. text file, with one record per row (`--input-type txt`)
2. a JSON file with an array of objects (`--input-type json`). You can specify which keys to use with the `--keydoc` and `--keyid` options which tell the script how to find the document text and the record ID.

### JSON schema file

You need to provide a JSON Schema file that will instruct ChatGPT how to transform the input text. Here's an example that I used:

```
{
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "name of person this document is from": {
      "type": "string"
    },
    "name of person this document is written to": {
      "type": "string"
    },
    "name of person this document is about": {
      "type": "string"
    },
    "violation": {
      "type": "string"
    },
    "outcome": {
      "type": "string"
    },
    "date": {
      "type": "string"
    },
    "summary": {
      "type": "string"
    }
  }
}
```

It can be helpful to name the fields in descriptive ways that ChatGPT can use to figure out what to extract.


[wrapper-main]: https://github.com/mmabrouk/chatgpt-wrapper
    "ChatGPT Wrapper - upstream version"

[playwright-setup]: https://playwright.dev/python/docs/library
    "Playwright - Getting Started"
