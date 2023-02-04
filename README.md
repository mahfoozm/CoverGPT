# CoverGPT
Generate a customized cover letter for a given job position, using your resume to add personalized details.

![image](https://user-images.githubusercontent.com/95328615/216740257-41b94c3d-3f1c-491d-ab5c-904d40a2033e.png)

## API Key
To use CoverGPT, you need a ChatGPT API key. To get one, make a ChatGPT account and go to [this link](https://platform.openai.com/account/api-keys). Generate an API key and set it in CoverGPT.

## Usage
Before generating your first cover letter, ensure that you have set your API key and filled out your user information. If you want a more personalized cover letter, upload your resume. You can still generate a cover letter without uploading your resume; but it will be of much lower quality.

## Using your own cover letter template
A LaTeX template is provided, but you can use your own if you wish. If you choose to use your own template, make the following replacements in your .tex file:
- First Name: #firstName
- Last Name: #lastName
- Website Link: #websiteUrl
- Email: #email
- Phone Number: #phoneNumber
- Full Name: #fullName
- Company Name: #companyName
- Company Address: #address1
- City, State/Province, Zip/Postal Code: #address2

### TO-DO:

- Considering a CoverGPT web app, to simplify usage.
