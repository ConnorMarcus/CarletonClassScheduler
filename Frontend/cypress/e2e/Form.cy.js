describe("Form Component", () => {
    beforeEach(() => {
        cy.visit('/');
        cy.injectAxe();
    });

    it("should display an error alert when no term is selected", () => {
        // Try and build schedule
        cy.get("#build-button").click();
        cy.get(".MuiAlert-message").should("exist").wait(100);
        cy.checkAccessibility();
    });

    it("should display an error alert when no courses are selected", () => {
        // Add first term
        cy.get("#term-select").click();
        cy.get(".MuiAutocomplete-popper li").eq(0).click();

        // Try and build schedule
        cy.get("#build-button").click();
        cy.get(".MuiAlert-message").should("exist").wait(100);
        cy.checkAccessibility();
    });

    it("should have no course options if a term is not selected", () => {
        // Open courses drop down and make sure its empty
        cy.get("#course-select-0").click();
        cy.get(".MuiAutocomplete-popper li").should("not.exist");
        cy.checkAccessibility();
    });

    it("should allow you to build a schedule", () => {
        // Spy on generateSchedules request
        cy.intercept("POST", "**/generateSchedules").as("generateSchedules");

        // Add first term and course
        cy.get("#term-select").click();
        cy.get(".MuiAutocomplete-popper li").eq(0).click();
        cy.get("#course-select-0").click();
        cy.get(".MuiAutocomplete-popper li").eq(0).click();

        // Build schedule then check for calendar component
        cy.get("#build-button").click().wait(1000);
        cy.wait("@generateSchedules").then((req) => {
            expect(req.response.statusCode).to.equal(200);
        });   
        cy.get("#calendar").should("exist");
        cy.checkAccessibility();
    });

    it("should clear the entire form when clear all is clicked", () => {
        // Add first term and course
        cy.get("#term-select").click();
        cy.get(".MuiAutocomplete-popper li").eq(0).click();
        cy.get("#course-select-0").click();
        cy.get(".MuiAutocomplete-popper li").eq(0).click();

        // Clear form
        cy.get("#clear-button").click();
        cy.get("#term-select").should("have.value", "");
        cy.get("#course-select-0").should("have.value", "");
        cy.checkAccessibility();
    });

    it("should allow you to add up to 5 daily filters", () => {
        cy.get("#add-button").should("be.enabled");
        // Add remaining 4 daily filters
        for (let i = 0; i < 4; i++) {
            cy.get("#add-button").click();
        }
        cy.get("#add-button").should("be.disabled");
        cy.checkAccessibility();
    });

    it("should allow you to remove up to 4 daily filters", () => {
        cy.get("#remove-button").should("be.disabled");
        // Add remaining 4 daily filters
        for (let i = 0; i < 4; i++) {
            cy.get("#add-button").click();
        }
        // Remove the 4 added daily filters
        for (let i = 0; i < 4; i++) {
            cy.get("#remove-button").click();
        }
        cy.checkAccessibility();
    });

    it("should remove calendar component when form is cleared", () => {
        // Add first term and course
        cy.get("#term-select").click();
        cy.get(".MuiAutocomplete-popper li").eq(0).click();
        cy.get("#course-select-0").click();
        cy.get(".MuiAutocomplete-popper li").eq(0).click();

        // Build schedule then check for calendar component
        cy.get("#build-button").click().wait(1000);
        cy.get("#calendar").should("exist");

        // Clear form and make sure calendar component is removed
        cy.get("#clear-button").click().wait(1000);
        cy.get("#calendar").should("not.exist");
        cy.checkAccessibility();
    });

    it("should remove calendar component when any input in the form is changed", () => {
        // Add first term and course
        cy.get("#term-select").click();
        cy.get(".MuiAutocomplete-popper li").eq(0).click();
        cy.get("#course-select-0").click();
        cy.get(".MuiAutocomplete-popper li").eq(0).click();

        // Build schedule then check for calendar component
        cy.get("#build-button").click().wait(1000);
        cy.get("#calendar").should("exist");

        // Change the course input and sure calendar component is removed
        cy.get("#course-select-0").click();
        cy.get("button[title='Clear']").eq(1).click().wait(1000);
        cy.get("#calendar").should("not.exist");
        cy.checkAccessibility();
    });
});