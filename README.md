# Government Grant Disbursement API

### Running the flask application:

* Clone the repository to your desired folder

```shell script
git clone https://github.com/mdanial1410/govtech-grant-api.git
```
Guide for Linux: [How to Clone a Git Repository in Linux](https://www.technipages.com/how-to-clone-a-git-repository-in-linux)

Guide for Windows: [How to Clone a GitHub Repository](https://www.howtogeek.com/451360/how-to-clone-a-github-repository/)

* Create a Python virtual environment (*optional*)

Guide For Linux: [How to Create Python Virtual Environments on Ubuntu 18.04](https://linuxize.com/post/how-to-create-python-virtual-environments-on-ubuntu-18-04/)

Guide For Windows: [Steps To Set Up Virtual Environment For Python On Windows](https://www.c-sharpcorner.com/article/steps-to-set-up-a-virtual-environment-for-python-development/)

* Install the necessary dependencies from the requirements file
```shell script
pip install -r requirements.txt
```

* Execute the flask application
```shell script
python3 app.py
```

* Testing the application

Use Postman to query the API

[Download Postman](https://www.postman.com/downloads/)

[Postman Tutorial for Beginners with API Testing Example ](https://www.guru99.com/postman-tutorial.html)

### Assumptions made in the project

The following assumptions were made in the project:
* Able to create a household without specifying family members
* For grant disbursement endpoint, search via household size
    * Households with matching size will be processed to determine the eligibility of all grants
    * Listing of household will only list by 'house_id'
    * Listing of qualifying members will only list by 'id' and 'name'
 