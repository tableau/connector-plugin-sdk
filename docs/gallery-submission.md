---
title: Connector Tableau Exchange Submission Guide
---

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

## Process overview
These are the steps you’ll take to prepare your connector and get it added to the Tableau Exchange:

1. Sign in to the Tableau Exchange website
2. Build and test your connector
3. Join the Tableau Partner Network
4. Fill out the form to create a connector listing
5. Submit source code and test artifacts via GitHub
6. Prepare go-to-market materials and submit them for review
7. Publish go-to-market materials when your connector launches

Building a connector generally takes two to six weeks, depending on complexity. Then, before it can be published to the Tableau Exchange, you'll submit it for approval. The approval process typically takes another two to six weeks.

## Get started

### (Optional) Join the Tableau Developer Program 

Joining the [Tableau Developer Program](https://www.tableau.com/developer) isn't required, but it does give you access to a free personal development sandbox with the latest pre-release version of Tableau Online.

### Step 1: Sign in to the Tableau Exchange website

Signing in to the Tableau Exchange website gets your account in our system, so that once you have completed the initial steps under Get Started, we can grant you the ability to add your connector.

1. Visit the [Tableau Exchange](https://exchange.tableau.com/) website.
2. Click **Sign In** in the upper-right corner.
3. If you already have a Tableau.com account, sign in with that account. At this time, signing in with Salesforce is not supported. If you don’t have a Tableau.com account, click **Create an Account**. To make it easier to verify your account, enter the same email address when signing up for a Tableau.com account, the Tableau Partner Network, and, if you have one, a Salesforce account.

### Step 2: Build and test your connector

Use the information in the [Connector SDK documentation]({{ site.baseurl }}/docs/) to build your connector. If you have issues with the SDK or need help, submit an issue through our [GitHub issues page]({{ site.baseurl }}/issues) and include the [required artifacts]({{ site.baseurl }}/docs/bug-artifacts) with the issue.

Be sure to test your connector with [the TDVT suite]({{ site.baseurl }}/docs/tdvt) to ensure that your connector meets our guidelines for connector functionality.

**Note:** The Tableau Exchange no longer accepts submissions of ODBC connectors. Only JDBC connectors are accepted.

### Step 3: Join the Tableau Partner Network

Join the Technology Track on our [Tableau Partner Network (TPN)](https://www.tableau.com/partners/become) after you’ve built your integration and are passing 90% of TDVT results (all tests [marked as required](https://github.com/tableau/connector-plugin-sdk/blob/master/tdvt/tdvt/metadata/priority.csv) should pass or should be acknowledged as not supported or a known bug for the underlying data source). By joining the TPN, you allow us to discuss confidential information with you and enable us to promote your products through our marketing channels, like the Tableau Exchange.

In order to be approved to submit your connector to the Tableau Exchange, complete the following tasks with the TPN. 

#### Get your connector reviewed by the TPN

Sign in to the [Partner Portal](https://partner.tableau.com/), then click on Partner Solutions to submit your connector for review. At this stage, you’ll need to provide a description, a brief demo, and a data sheet showing how your connector works with Tableau. You'll later provide more materials and details about your connector to add it to the Tableau Exchange.

#### Join the Tableau Partner TSANet

All technical partners who want to add connectors to the Tableau Exchange must join the Tableau Partner Technical Support Alliance Network (TSANet). TSANet provides a platform that allows Tableau to address customer issues in collaboration with our partners.

#### Sign the Tableau Exchange Agreement

After the TPN has reviewed your connector, we will send you a copy of the Tableau Exchange Agreement.

All Tableau Exchange Agreements are processed through Service Now. A copy of the Tableau Exchange agreement should be reviewed and approved by the person who will process the agreement on your side. To process the agreement, we will need:
- Legal name of your company
- Name of the signee
- Title of signee
- Email address of signee (Docusign is sent to this person)

## Submit your connector to the Tableau Exchange 

### Security considerations for connectors
As part of the connector review we will perform a security review of your connector. Read the [Security Considerations]({{ site.baseurl }}/docs/security-considerations) to make sure that your connector will be accepted. Connectors with security vulnerabilities will not be approved for the Tableau Exchange until a fix is provided, and connectors already posted to the Tableau Exchange that are found to have security vulnerabilities will be pulled until a fix is provided.

### Step 4: Fill out the form to create a connector listing

1. Sign in to the [Tableau Exchange](https://exchange.tableau.com/) website.
2. Click on your initials in the upper-right corner and select **Contributor Console**. If you don't have access to the contributor console, reach out to the Tableau Partner Network for help. If other members of your organization already have access to the contributor console, they can also give you access.
2. On the Contributor Console, click the **Create** button then select **Connector**.
3. Fill out the form for your connector, following the guidance under [Tableau Exchange submission materials and details](#tableau-exchange-submission-materials-and-details).
4. To see what your connector listing will look like, click the **Preview** button at the bottom of the form. 
5. Once you are satisfied with your listing, click **Request Approval**.

### Tableau Exchange submission materials and details

All of the following materials are required for submission of a connector to the Tableau Exchange unless stated otherwise. Submitting these materials and signing the Tableau Exchange Agreement does not guarantee the addition of a connector to the Tableau Exchange.

#### Listing name

Include the name for your application/database to which the connector connects.

#### Icon

Submit an icon representing your application or database. This should be easily recognizable as a representation of your application or database. Must be 280x280 pixels and in PNG, JPEG, GIF, or SVG format.

#### Short description

Briefly describe details about your connector that are most relevant for customers. This description displays on the main [Connectors page](https://exchange.tableau.com/connectors) of the Tableau Exchange. Maximum 116 characters. Plain text only.

#### Detailed description

For your connector’s detail page, provide a long description. Include these three parts.

- A description of your application or database.
- A description of your connector’s competitive advantage over Other ODBC/JDBC connectors.

   Example:

   _This connector provides a smooth and easy way to connect to Google Big Query. By using this connector, customers can leverage Google's internal storage and extract APIs, which offer up to 10x performance increases when extracting large amounts of data. This connector also allows users to use custom OAuth, which is not currently supported natively with an Other JDBC connection._
- Known issues or version requirements for the connector.

Markdown for this field is supported. We encourage you to submit a robust long description so that customers understand why they should download your connector.

#### Installation instructions

Installation instructions have two parts:

- Tableau installation
  * Installing the TACO file
  * Installing the driver
- Your custom installation instructions

To make things easy, we created templates for your custom installation instructions. These templates, linked below, are markdown friendly. If you have additional installation instructions, append them below the Tableau installation instructions.
* [Tableau Desktop Installation Instructions JDBC Template](./templates/tableau-desktop-jdbc-template.md)
* [Tableau Prep Builder Installation Instructions JDBC Template](./templates/tableau-prep-jdbc-template.md)
* [Tableau Server Installation Instructions Template](./templates/tableau-server.md)

#### TACO file

Upload the TACO file for your connector. Information in this file should match the information submitted on the form. TACO files must be [signed by a certificate authority]({{ site.baseurl }}/docs/package-sign#sign-your-packaged-connector-with-jarsigner) to be accepted. The certificate must be signed with a timestamp that will be valid for the next 5 years.

#### Terms of service

Include an agreement between you and the users of your connector. Includes regulations on how your connector can be used, usage restrictions, availability, liability provisions, and so on. The same terms of service can be used across multiple listings on the Tableau Exchange. PDF or URL.

#### Privacy policy

Include an agreement between you and the users of your connector. Can be a link to your existing company’s privacy policy. Should outline your data handling policies. The same privacy policy can be used across multiple listings. PDF or URL.

#### Support URL

Include a link to a website or email address where users can get help troubleshooting issues. Preferably a page where users can file a support ticket or the email address of your support team. This should not be the home page of your website.

#### Driver download 

Include either a link to download the driver or brief instructions on how to get the driver. 

#### Beta status 

Select the **Beta** checkbox if you want to display a “Beta” badge on your connector. There is no official beta program for connectors. It's up to you to decide when your connector is ready to go from beta to general availability.

#### Supported languages

Select **English**. 

#### Pricing model

Select **Free**. All connectors are free at this time.

#### Localization options

By default, the information you submit about your connector will be localized, with the exception of the connector name. To opt out of localization, select **Do not localize any fields**. To localize your connector name, select **Localize listing name**.

#### Scheduled publish date

If you would like your connector to be published on a certain date, select that date. Be aware when selecting a date that the approval process for a connector takes two to six weeks.

### Step 5: Submit source code and test artifacts via GitHub

#### GitHub username or email

Share your GitHub username or email with your TPN account manager, and we will create a GitHub repository for you to share your source code and test artifacts. 

#### Connector source code

Provide the unzipped source files for your connector so we can review each file.

#### TDVT files 

[The TDVT suite]({{ site.baseurl }}/docs/tdvt) produces a number of important files required for a review. Provide the following files.

- TDVT results csv file (test_results_combined.csv)
- TDVT logs (tdvt_log_combined.txt, tabquery_logs.zip, and tdvt_actuals_combined.zip)
- TDVT environment (INI config file)

TDVT tests can be skipped for extract-only connectors.

In most cases, TDVT should be passing more than 90% of test cases to be accepted. All tests [marked as required](https://github.com/tableau/connector-plugin-sdk/blob/master/tdvt/tdvt/metadata/priority.csv) should pass or should be acknowledged as not supported or a known bug for the underlying data source.


#### QA artifacts

Provide the following artifacts to show that your connector has passed manual QA tests.

- Screenshots or a video of you going through the manual QA tests listed on [Run Manual QA Tests]({{ site.baseurl }}/docs/manual-test).
- Clean logs that show the test cases being done.
  * "Clean logs" mean that, for Tableau Desktop, you deleted everything in "My Tableau Repository\Logs" before running through the tests.
  * For Tableau Server, you can use a tsm command to create a zipped archive of all log files. For more information, see [Server Log Files in a zipped archive](https://help.tableau.com/current/server/en-us/logs_loc.htm#server-log-files-in-a-zipped-archive).

#### Vendor fields

List of all vendor-defined fields (vendor1 , vendor2, and vendor3 in a .tcd file, or fields with a “v-” prefix in connection fields) in PDF, DOC, or DOCX format. Define what the fields are, give sample input, and confirm that they can never contain personally identifiable information (PII). 

#### Verification that TACO file is signed

Include a screenshot or text file of the full output of the command `jarsigner -verify path_to_taco -verbose -certs -strict` to show that your connector is signed by a trusted certificate authority. For more information, see [Get your connector signed]({{ site.baseurl }}/docs/package-sign#get-your-connector-signed).

## Go to market 

### Step 6: Prepare go-to-market materials and submit them for review

Partners are welcome to publish blog posts and press releases announcing the availability of their connector on the Tableau Exchange. Marketing materials should specify the joint-value proposition of the offering and tell the story of how your Tableau integration is uniquely suited to solve customer challenges. 

Once customers are benefitting from your Tableau integration, we’ve found public customer case studies to be the most impactful method for promoting joint-solutions. The best performing customer case studies are evergreen and applicable to a broad number of customers by demonstrating how your integration solves for pain points commonly experienced across your industry. Typically, case studies are hosted on our partner’s sites.

**Blog posts and press releases**
- Review the Tableau Partner Brand Guidelines accessible via the Partner Portal.
- Draft your blog post and/or press release and submit it to the Partner Marketing team via email to [partnermarketing@tableau.com](mailto:partnermarketing@tableau.com) for initial review.
  * We require at least a two-week approval timeline.
- If you would like, please include a suggested quote attributed to a Tableau spokesperson. Tableau reserves the right to make edits and will also help determine the appropriate spokesperson.

**Customer case studies**
- Submit your customer case study via the Partner Portal.
- Examples of quality case studies can be found on [Tableau Customer Stories](https://www.tableau.com/solutions/customers?utm_campaign_id=2017049&utm_campaign=Prospecting-ALL-ALL-ALL-ALL-ALL&utm_medium=Paid+Search&utm_source=Google+Search&utm_language=EN&utm_country=USCA&kw=&adgroup=CTX-Trial-Solutions-DSA&adused=DSA&matchtype=&placement=&d=7013y000000vYhH&gclid=Cj0KCQjwxtSSBhDYARIsAEn0thSVm6r1Gf3jy7oz8rRi8r6j4q3zSMF8CU5lCZCHPeUExa4pYnE7XcUaAmM7EALw_wcB&gclsrc=aw.ds).

**Social media**
- There are no guarantees our brand social team can engage/amplify every and all partner social media posts, but partners are welcome to tag us on both [LinkedIn](https://www.linkedin.com/company/tableau-software) and Twitter ([@Tableau](https://twitter.com/tableau)) for consideration. 


## Launch your connector

### Step 7: Publish go-to-market materials when your connector launches

Once your connector is approved, you will receive an email notification. You can now publish your Tableau-approved go-to-market materials to let your customers know that the connector is available.

### Step 8: Update your connector, as needed

If you need to update your connector, make changes using the same form you used to submit it to the Tableau Exchange. Any changes you make will require approval before they are published. 

If your connector is a beta release, be sure to update the connector when you are ready to move it from beta to general availability.

To update your connector:
1. Sign in to the [Tableau Exchange](https://exchange.tableau.com/) website.
2. Click on your initials in the upper-right corner and select **Contributor Console**.
3. Under the list of published listings, find your connector and open it.
4. Make your updates to the connector information.
5. Click **Request Approval**.

After you've updated your connector listing, provide the following items for review on the GitHub repository where you originally submitted your source code:
- Video or screenshots of you running the [QA tests for a connector update]({{ site.baseurl }}/docs/manual-test#test-a-connector-update)
- [Verification that your TACO file is signed](#verification-that-taco-file-is-signed)

Depending on the changes that you made to the connector, we might need to conduct a full technical review. In that case, you will need to provide additional materials from those listed under [Step 5: Submit source code and test artifacts via GitHub](#step-5-submit-source-code-and-test-artifacts-via-github). 