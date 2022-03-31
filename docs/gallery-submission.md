---
title: Connector Tableau Exchange Submission Guide
---

**Note:** Download a PDF version of this guide [here]({{ site.baseurl }}/assets/Connector-Gallery-Submission-Guide.pdf).

> ![]({{ site.baseurl }}/assets/tableau-logo.png)
>
> Thanks for your interest in submitting a connector for Tableau Exchange. This document describes the steps and assets required to submit your
> connector to [Tableau Exchange](https://exchange.tableau.com/). While this is a self-service process, feel free to contact us if you need assistance.
>
>Best regards -- The Tableau Team
>
---
**In this section**

* TOC
{:toc}

## Process Overview

These are the steps you'll take to prepare and submit your connector to Tableau Exchange:

1. Join the Tableau Developer Program.
2. Build your integration.
3. Sign up for the Technology Partner Program.
4. Submit a request to publish your connector in Tableau Exchange.
5. Sign the Tableau Exchange Agreement.
6. Submit TDVT results and get approval for your connector.
7. Prepare Go-to-Market assets and get content approved by Tableau.
8. Release connector in Tableau Exchange for beta testing.
9. Get beta-testing feedback from five customers.
10. Launch the connector in Tableau Exchange and publish Go-To-Market materials.

Building a connector generally takes two to six weeks, depending on complexity. Then, before it can be published to Tableau Exchange, you'll need to submit the connector and beta test it. This typically takes another two to four weeks.

![]({{ site.baseurl }}/assets/timeline.png)

Note: As part of the connector review we will perform a security review of the connector. Please read the [Security Considerations]({{ site.baseurl }}/docs/security-considerations) page to make sure your connector will be accepted. Connectors with security vulnerabilities will not be approved for the Exchange until a fix is provided, and connectors already posted to the Exchange that are found to have security vulnerabilities will be pulled until a fix is provided.

---

## Getting Started

### Step 1: Join the Tableau Developer Program


Join our [Tableau Developer Program](https://www.tableau.com/developer) to gain access to a free development sandbox.

### Step 2: Build your integration

After you've signed up for our developer program, use the information in this Connector SDK documentation to get started building a connector. If you have issues with the SDK or need help, submit an issue through our [GitHub issues page](https://github.com/tableau/connector-plugin-sdk/issues).

Be sure to test your connector with the [TDVT suite](https://tableau.github.io/connector-plugin-sdk/docs/tdvt) to ensure that your connector meets our guidelines for connector functionality.

**Note:** The Tableau Exchange no longer accepts submissions of ODBC connectors. Only JDBC connectors are accepted.

## Submitting Your Connector to Tableau Exchange

### Step 3: Sign up for Technology Partner Program

After you've built your integration and are passing 90% of TDVT results, sign up for our [Technology Partner Program](https://www.tableau.com/partners/resources/technology/partner-agreement). By signing up for the Technology Partner Program you allow us to discuss confidential information with you and enables us to promote your products through our marketing channels, like Tableau Exchange.

### Step 4: Submit a Request to Publish

After you've built and tested your integration, [submit a request](https://forms.gle/2FisXfmwwuQEaXKG9) to publish your connector in Tableau Exchange.

### Step 5: Sign Tableau Exchange Agreement

When we receive your request to publish, we will send you:
 - A copy of the Tableau Exchange Agreement
 - A submission form for your TDVT results, plus  other Tableau Exchange submission materials

---

### Tableau Exchange Submission Materials

_All of the following materials are required for submission of an extension into Tableau Exchange unless stated otherwise. Submission of these materials and signing of the agreement does not guarantee the addition of an extension to Tableau Exchange._

[_Submit a Connector to Tableau Exchange via Google Tables_](https://tables.area120.google.com/u/0/form/aazkn9dCirC305k3Czjkoa/t/aTDxX-eQDxddDrdwaKi4X18Wrn9R7TiQQ9mm_2PBJkUtb2RwGj3__s5bdc0rDX6_c0)

##### Signed Agreement

All Tableau Exchange agreements are processed through Service Now. A copy of the Tableau Exchange agreement should be reviewed and approved by the person who will process the agreement on your side. To process the agreement, we will need:

- Legal name of your company
- Name of the signee
- Title of signee
- Email address of signee (Docusign is sent to this person)

##### TACO File

Include a copy of the manifest file (.taco) for your connector. Information in this file should match the information submitted for the items below. TACO files must be [signed by a certificate authority](https://tableau.github.io/connector-plugin-sdk/docs/log-entries) to be accepted.

##### TDVT Results and Explanations of Failures

TDVT will produce a number important files required for a review:

- test\_results\_combined.csv (CSV is preferred)
- tdvt\_log\_combined.txt
- tdvt\_actuals\_combined.txt
- tdvt\_output\_combined.txt
- tabquery\_logs.zip

In most cases, TDVT should be passing more than 90% of test cases to be accepted. A summary of failed test cases should be provided for review.

##### Connector Name

Include the name for your application/database to which the connector connects .

##### Short Description

Briefly describe details about your connector that are most relevant for customers. This displays on the main Connectors page of Tableau Exchange. Maximum 116 characters. Plain text only.

##### Long Description

For your connector's detail page, provide a long description. Include these three parts.

- A description of your application or database.
- A description of what the connector does that makes better than using an Other ODBC/JDBC connection.

   Example:

   _This connector provides a smooth and easy way to connect to Google Big Query. By using this connector, customers can leverage Google's internal storage and extract APIs, which offer up to 10x performance increases when extracting large amounts of data. This connector also allows users to use custom OAuth, which is not currently supported natively with an Other JDBC connection._
- Known issues or version requirements for the connector

Markdown for this field is supported. We encourage partners to submit a robust long description so that customers understand why they want to download the connector.

##### Installation Instructions

Installation instructions have two parts:

- Tableau installation
  * Installing the TACO file
  * Installing the driver
- Your custom installation instructions

To make things easy, we created templates for your custom installation instructions. These templates, linked below, are markdown friendly. If you have additional installation instructions, append them below the Tableau installation instructions.
* [Tableau Desktop Installation Instructions JDBC Template](./templates/tableau-desktop-jdbc-template.md)
* [Tableau Prep Builder Installation Instructions JDBC Template](./templates/tableau-prep-jdbc-template.md)
* [Tableau Server Installation Instructions Template](./templates/tableau-server.md)

##### Icon

Submit an icon representing your application or database. This should be easily recognizable as a representation of your application or database. Must be 280x280 pixels, PNG format.

##### Screenshots (optional)

Include larger images displaying any custom functionality of using your connector, or a screenshot of your application/database product. These images can also be used to help support custom installation instructions required on the application/database side. You can submit up to three. Must be 1200x680 pixels, PNG or GIF format. Can be animated. Images are encouraged to enhance the user experience, but are not required.

##### Privacy Policy

Include an agreement between you and the customers using your connector. Can be a link to your existing company's privacy policy. Should outline your data handling policies. The same Privacy Policy can be used across multiple listings. PDF or URL.

##### Terms of Service

Include an agreement between you and the customers using your connector. Includes regulations on how your extension can be used, usage restrictions, availability, liability provisions, and so on. The same Terms of Service can be used across multiple extensions. PDF or URL.

##### Support Link

Include a link to a website or email address where users can easily get help troubleshooting issues. Preferably a page where users can file a support ticket or email address of your support team. This should not be the home page of your website.

##### *Optional:* GitHub Repository

If your connector is open source, provide the link to your GitHub repository.

##### Beta Feedback Email Addresses

Inlcude a short list of email addresses to give access to the Beta feedback. Should be internal to your company only.

---

### Step 6: Submit TDVT Results and get connector approved

Complete the submission form and return it with your TDVT results to Tableau.


---
## **Go to Market**

### Step 7: Prepare Go-to-Market activities and get content approved by Tableau

Many partners choose to put out blogs and a press release once they offer custom connectors for their customers in Tableau Exchange. To fully promote your work, we recommend collecting a public customer case study that highlights the advantages and usefulness of your new connector. Not only does Tableau have mechanisms and channels to promote your customer case study, but historical data shows that referencing customer case studies generate on average five times more traffic than standalone blogs.

We are happy to support partners looking to issue Tableau-specific press releases. We require that any partner press release mentioning Tableau is first submitted for approval to ensure that the Tableau positioning and branding are accurate.

**Tableau PR requires a 2-week approval timeline for press releases.**

The process:

1. Partner drafts a press release using the Tableau Partner Brand Guidelines (available to partners in the PDC).

Note: The release should not include the Tableau corporate boilerplate.
2. Partner submits the draft to the Partner Marketing team via email (partnermarketing@tableau.com) for initial review.
3. The Partner Marketing team contacts Tableau PR for a full review and legal sign-off.

**Note** : We consider quote attribution from a Tableau spokesperson on a case-by-case basis. Press releases that announce milestone product launches and significant customer successes are typically reviewed to determine relevant quote attribution. For these types of releases, the partner can include a proposed Tableau quote as part of the draft for consideration.


---
## **Beta Process**

### Step 8: Release connector in Tableau Exchange for beta testing.

When your connector is approved, it will be released to Tableau Exchange for beta testing.

### Step 9: Get beta-testing feedback from five customers.

After your connector is added to Tableau Exchange, you'll need to beta-test your connector with at least **five customers** before your connector can move to a General Audience (GA) release. While you'll be able to catch most issues with the TDVT suite, customer testing helps refine your results. Customers often have unique environments that need to be tested to ensure that everything works as expected.

Customers can find our beta test scenarios and [Beta feedback form](https://forms.gle/xjWGk86tv8eD43Mk7) on the feedback button in Tableau Exchange. Note that the feedback form is specific to your connector, and you will be able to monitor the progress of the beta test on your own. The total beta testing process shouldn't take more than 30 minutes for a customer to complete.

To pass from beta into a General Audience release, all customers must submit feedback saying that there were no blocking issues with creating or publishing workbooks on Tableau Desktop and Server. If any issues are encountered, you will need to fix them, send us your new TACO file, and have those customers rerun the beta test scenarios.


---
## Launch Your Connector

### Step 10: Launch the connector in Tableau Exchange and publish Go-To-Market materials.

After your beta testing phase is finished and your go-to-market materials are planned, contact Tableau to choose the date and time your connector will be pushed to production.
