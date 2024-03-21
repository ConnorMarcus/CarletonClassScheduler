describe("App tests", () => {
    beforeEach(() => {
        cy.visit("/");
    });

    it("should render the LandingPage, Form & Footer initially with no errors", () => {
        cy.get(".landing-page").should("exist");
        cy.get("#form-component").should("exist");
        cy.get(".footer").should("exist");
    });

    it("should have successful responses for the term & courses api", () => {
        cy.intercept("GET", "**/getTerms").as("getTerms");
        cy.intercept("GET", "**/getCourses?Term=Fall*").as("getFallCourses");
        cy.intercept("GET", "**/getCourses?Term=Winter*").as("getWinterCourses");
        cy.intercept("GET", "**/getCourses?Term=Summer*").as("getSummerCourses");

        cy.wait("@getTerms").then((req) => {
            expect(req.response.statusCode).to.equal(200);
        });      
        cy.wait("@getFallCourses").then((req) => {
            expect(req.response.statusCode).to.equal(200);
        });  
        cy.wait("@getWinterCourses").then((req) => {
            expect(req.response.statusCode).to.equal(200);
        }); 
        cy.wait("@getSummerCourses").then((req) => {
            expect(req.response.statusCode).to.equal(200);
        });  
    });

    it("should display the correct content on the LandingPage", () => {
        cy.get("h2").eq(0).should("exist")
            .and("contain", "Welcome to the Carleton UniversityStudent Scheduler Tool");
        cy.get("a").contains("Build Your Schedule").should("exist");
        cy.get("a").contains("Need Assistance").should("exist");
    });

    it("should navigate to the correct section when 'Build Your Schedule' button is clicked", () => {
        cy.get("a").contains("Build Your Schedule").click();
        cy.url().should("include", "#form-component");
    });

    it("should display the correct content in the footer", () => {
        cy.get(".MuiTypography-body1").should("exist")
            .and("contain", "© 2024 CarletonClassScheduler. All rights reserved.");
        cy.get("a").contains("View on GitHub").should("exist");
    });
});