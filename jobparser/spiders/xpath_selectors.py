

PAGE_XPATH = {
    'pagination_button': '//div[@data-qa="pager-block"]//a[@data-qa="pager-page"]/@href',
    'vacancy_page': '//div[contains(@data-qa, "vacancy-serp__vacancy")]//a[@data-qa="vacancy-serp__vacancy-title"]/@href',
}

VACANCY_DATA_XPATH = {
        'title': '//h1[@data-qa="vacancy-title"]/text()',
        'salary': '//p[@class="vacancy-salary"]//text()',
        'description': '//div[@class="vacancy-description"]//text()',
        'skills': '//div[contains(@data-qa, "skills-element")]//text()',
        'employer_url': '//a[@data-qa="vacancy-company-name"]/@href',
}

EMPLOYER_DATA_XPATH = {
        'name': '//span[@data-qa="company-header-title-name"]/text()',
        'site': '//a[@data-qa="sidebar-company-site"]/@href',
        'business_fields': '//div[@class="employer-sidebar-block"]/p/text()', #сферы деятельности
        'description': '//div[@class="company-description"]//text()',
        #'vacancies_url': '//div[@class = "employer-sidebar"]//a[@data-qa = "employer-page__employer-vacancies-link"]'
    }
