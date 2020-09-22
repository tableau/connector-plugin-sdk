---
title: Connector Gallery Submission Guide
---

**Note:** Download a PDF version of this guide [here]({{ site.baseurl }}/assets/Connector-Gallery-Submission-Guide.pdf).

<br />

![]({{ site.baseurl }}/assets/tableau-logo.png)

Thanks for your interest in submitting a connector for the Extension Gallery. This document will walk you through the publishing steps and the assets required to submit your Connector to the [Extension Gallery](https://extensiongallery.tableau.com/connectors). This process was built to be as self-service as possible, but there are many opportunities for touchpoints with our team along the way if you get stuck or need help.

---


## Process Overview

Building a connector generally takes 2 - 6 weeks depending on complexity. Once the connector is built, the connector approval and beta process combined usually take 2 - 4 additional weeks prior to publication.

1. Join Developer Program
2. Start building your integration
3. Sign up for Technology Partner Program
4. Submit a request to publish your Connector in the Extension Gallery
5. Sign Gallery Agreement
6. Submit TDVT Results and get connector approved
7. Prepare Go-to-Market activities and get content approved by Tableau
8. Release connector in Gallery in Beta
9. Get feedback from 5 customers through Gallery Beta Feedback
10. Launch connector in the Gallery and publish GTM materials 

![]({{ site.baseurl }}/assets/timeline.png)

---

## Getting Started

1. Join Developer Program
2. Build your integration

Join our [Tableau Developer Program](https://www.tableau.com/developer) to gain access to a free development sandbox. Once you've signed up for our developer program, check out our [Connector SDK documentation](https://tableau.github.io/connector-plugin-sdk/) materials which will provide you with what you need to get started building a connector. If you encounter issues with the SDK or need help, submit an issue through our GitHub issues page. You should [use TDVT](https://tableau.github.io/connector-plugin-sdk/docs/tdvt) to ensure that your connector meets our guidelines for connector functionality.

## Submitting Your Connector to the Extension Gallery

3. Sign up for Technology Partner Program
4. Submit a request to publish your Connector in the Extension Gallery
5. Sign Gallery Agreement
6. Submit TDVT Results and get connector approved

Once you've built your integration and are passing 90% of TDVT results, sign up for our [Technology Partner Program](https://www.tableau.com/partners/resources/technology/partner-agreement). By signing up for the Technology Partner Program you allow us to discuss confidential information with you and enables us to promote your products through our marketing channels, like the Extension Gallery, and gives you access benefits such as demo licenses, discount codes for training, and more!

After you've built your integration, you should [submit a request](https://forms.gle/2FisXfmwwuQEaXKG9) to publish your Connector in the Extension Gallery. From there we will send you a copy of the Extension Gallery Agreement and a form where you can submit your TDVT results and other Gallery Submission Materials.

---

## Extension Gallery Submission Materials

_All of the following materials are required for submission of an extension into the Extension Gallery unless stated otherwise. Submission of these materials and signing of the agreement does not guarantee the addition of an extension to the Gallery._

[_https://airtable.com/shrTBaQKvKAUElF5e_](https://airtable.com/shrTBaQKvKAUElF5e)

### Signed Agreement

All Extension Gallery agreements are executed through Service Now. A copy of the Gallery agreement should be reviewed and approved by the person who will execute the agreement on your side. To execute the agreement we will need:

- Legal name of your company
- Name of the signee
- Title of Signee
- Email address of signee (to send Docusign to)

### TACO File

The manifest file for your connector. Information in this file should match the information submitted for the items below. Taco files need to be [signed by a certificate authority](https://tableau.github.io/connector-plugin-sdk/docs/log-entries) to be accepted.

### TDVT results &amp; explanations of failures

TDVT will produce a number important files required for a review:

- test\_results\_combined.csv (note: CSV is preferred)
- tdvt\_log\_combined.txt
- tdvt\_actuals\_combined.txt
- tdvt\_output\_combined.txt
- tabquery\_logs.zip

TDVT should be passing more than 90% of test cases in order to be accepted for the majority of cases. A summary of failed test cases should be provided for review.

### Connector Name

The name for your application/database that the connector connects to.

### Short Description

A short blurb about your connector which is most relevant for customers, only shown on the front page. Maximum 116 characters. Plain text only.

### Long Description

Long descriptions have 3 parts.

1. A description of your application or database.
2. A description of what the connector does that makes better than using an Other ODBC/JDBC connection
  1. Example may be: This connector provides a smooth and easy way to connect to Google Big Query. By using this connector, customers will have the ability to leverage Google's internal storage and extract APIs which offer up to 10x performance increases when extracting large amounts of data. This connector also allows users to use custom OAuth which is not currently supported natively with an Other JDBC connection.
3. Known issues or version requirements for the connector

Markdown for this field is supported. We encourage partners to submit a robust long description so that customers understand why they want to download the connector.

### Installation Instructions

Installation instructions have 2 parts:

1. Tableau installation
  * Installing the .taco file
  * Installing the driver
2. Your custom installation instructions

To make things easy, we've created a template for your custom installation instructions (included below, markdown friendly). Any additional installation instructions should be appended below the Tableau installation instructions.

| **JDBC** | **ODBC** |
| ----------- | ----------- |
| <pre> 1. Download the Connector file (.taco).<br /> 2. Move the .taco file here:- Windows: C:\Users\[Windows User]\Documents\My Tableau Repository\Connectors- macOS: /Users/[user]/Documents/My Tableau Repository/Connectors<br />3. Start Tableau and under \*\*Connect\*\*, select the Connector Name connector. (\*\*Note:\*\* You'll be prompted if the driver is not yet installed. <br />4. Connector Name Driver Installation:<br />- A. Go to the [Driver Download](https://www.driverdownloadlinkhere.com)<br />- B. Download the Connector Name Driver .jar file and move into the following directory:- Windows - C:\Program Files\Tableau\Drivers- macOS - /Users/[user]/Library/Tableau/Drivers5. Relaunch Tableau and connect using the Connector Name connector. </pre> | <pre> 1. Download the Connector file (.taco). <br />2. Move the .taco file here:- Windows: C:\Users\[Windows User]\Documents\My Tableau Repository\Connectors <br />3. Start Tableau and under \*\*Connect\*\*, select the Connector Name connector. (\*\*Note:\*\* You'll be prompted if the driver is not yet installed.) <br />4. Connector Name Driver Installation: <br />- A. Go to the [Driver Download](https://www.driverdownloadlinkhere.com) <br />- B. Download the Connector Name Driver and install following the instructions in the readme provided with the client install. Ensure the 64-bit Client version is installed. <br />5. Relaunch Tableau and connect using the Connector Name connector. </pre> |


### Icon

An icon representing your application/database. Should be able to easily recognize the application/database. Must be 280x280 pixels, PNG format.

### Screenshots

Larger images displaying any custom functionality of using your connector, or a screenshot of your application/database product. These images can also be used to help support custom installation instructions required on the application/database side. Can have up to three. Must be 1200x680 pixels, PNG or GIF format. Can be animated. Images are encouraged to enhance the user experience, but are not required.

### Privacy Policy

An agreement between you and the customers using your connector. Can be a link to your existing company's privacy policy. Should outline your data handling policies. The same Privacy Policy can be used across multiple listings. PDF or URL.

### Terms of Service

An agreement between you and the customers using your connector. Includes regulations on how your extension can be used, usage restrictions, availability, liability provisions, etc. The same Terms of Service can be used across multiple extensions. PDF or URL.

### Support Link

A link to a website or email address where users can easily get help troubleshooting issues. Preferably a page where users can file a support ticket or email address of your support team. This should not be the home page of your website.

### *Optional:* GitHub Repository

If your connector is open-source please provide us with the link to your GitHub repository.

### Beta Feedback Email Addresses

A short list of email addresses to give access to the Beta feedback. Should be internal to your company only.

Beta Process and Preparing Your Go-to-Market Materials

---
## **Beta Process and Preparing Go-to-Market Materials**

Upon acceptance into the Extension Gallery, you'll need to Beta test your connector with at least 5 customers to move to a General Audience (GA) release. TDVT does a great job in catching most issues with connectors, but customers often have unique environments that need to be tested to ensure that everything works as expected. Because of this we request that you reach out to 5 unique customers to test your connector. Customers can find our Beta test scenarios and [Beta feedback form](https://forms.gle/xjWGk86tv8eD43Mk7) on the feedback button in the Extension Gallery. Note that the feedback form is specific to your connector, and you will be able to monitor the progress of the Beta on your own. The total beta testing process shouldn't take more than 30 minutes for a customer to complete.

In order to pass from Beta into GA all customers must submit feedback saying that there were no blocking issues with creating or publishing workbooks on Tableau Desktop and Server. If any issues are encountered, you will need to fix them, send us your new .taco file, and have those customers re-run the beta test scenarios.

---
## **Partner-Led GTM Activities**

We’re really excited to start working with you on go-to-market activities! We’ve outlined several ways in which we can get the word out about the great things that we’re doing together. 

It’s important that you’ve joined our technology partner program and have access to our [Partner Portal](https://partner.tableau.com/) to take advantage of the marketing materials that we have for our partners in the ‘[Activate Marketing Campaigns](https://partners.tableau.com/)’ section as well as assets to get started. If you’re already a partner and need access to the Partner Portal, you can reach out to [partners@tableau.com](mailto:partners@tableau.com). 

Note that for joint GTM activity, such as a webinar, we like to have a few published joint customer case studies with the partner first. This helps us to ensure we have assets that help explain the value of our joint solution and to understand how these types of activities could fit into our greater integrated campaigns. 

**1. Out-of-the-box Campaign**

To explore go-to-market activities, the best first step is to review the resources available to you in the Partner Portal.  If you go to “Activate Marketing Campaign” within the portal’s Partner Demand Center (PDC), you’ll find some out-of-the box campaigns that you can leverage (templates for landing pages, emails, and content syndication pages). Most Technology Partners use the “Create your own” Campaigns so they can insert their own messaging. If you are interested in learning more on how to best leverage the PDC, feel free to check out this [webinar](https://www.tableau.com/sites/default/files/partner_demand_center_training_webinar.mp4). 

**2. Blog Post** 

Blog posts are an easy way for our partners to announce our integration partnership and increase our awareness in the market. You’re at liberty to structure the post however you see fit, but here are a few points to writing a successful post:
- Focus on customer value. 
- Shouldn’t be overly technical in nature. It should complement documentation that’s available elsewhere. 
- A picture is worth a thousand words. Screenshots, gifs, or videos can help illustrate value. 
- Customer quotes validate the solution. See #3 on [Customer Evidence]().

Please utilize the [Tableau Partner Brand Guidelines](https://www.tableau.com/sites/default/files/media/tableaupartners_brandstyleguide.pdf) (in the partner portal under ‘Activate Marketing Campaign’) 

Examples of blog posts are partners have written announcing their new integrations: 
- [Dremio's new connector](https://www.dremio.com/announcing-dremion-on-the-tableau-extension-gallery/)
- [Arria's new extension](http://blog.arria.com/in-the-news/arria-now-featured-on-the-tableau-extension-gallery)
- [Collibra's customer success with Lockheed Martin](https://www.collibra.com/blog/lockheed-martins-journey-to-data-intelligence)

**3. Press Release**

We are happy to support partners looking to issue a Tableau-specific press release. We require that any partner press release mentioning Tableau is first submitted for approval to ensure that the Tableau positioning and branding is accurate. 
 
Tableau PR requires a 2-week approval timeline for press releases. 
 
The process: 
1. The partner drafts a press release utilizing the [Tableau Partner Brand Guidelines](https://www.tableau.com/sites/default/files/media/tableaupartners_brandstyleguide.pdf) (in the partner portal under ‘Activate Marketing Campaign’) Note: The release should not include the Tableau corporate boilerplate. 
2. Partner submits the draft to the Partner Marketing team via email ([partnermarketing@tableau.com](mailto:partnermarketing@tableau.com)) for initial review. 
3. Next, the Partner Marketing team will reach out to Tableau PR for a full review and legal sign off. 

Note: We consider quote attribution from a Tableau spokesperson on a case-by-case basis. Press releases that announce milestone product launches and significant customer successes are typically reviewed to determine relevant quote attribution. For these types of releases, the partner can include a proposed Tableau quote as part of the draft for consideration. 

---
## Launch Your Connector

Once your Beta is finished and your GTM materials are planned reach out to your contact and let them know the date and time you want your Connector to be pushed to production. Now sit back and enjoy!!!