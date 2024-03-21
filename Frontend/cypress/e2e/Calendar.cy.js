describe("Calendar Component", () => {
    beforeEach(() => {
        cy.visit("/");
    });
    
    it("should NOT display an alert when the 25 schedule limit is NOT hit", () => {
        // Build a Schedule for Fall with SYSC 2006
        cy.get("#term-select").click().type("Fall");
        cy.get(".MuiAutocomplete-popper li").eq(0).click();
        cy.get("#course-select-0").click().type("SYSC 2006");
        cy.get(".MuiAutocomplete-popper li").eq(0).click();
        cy.get("#build-button").click().wait(1000);

        cy.get(".MuiAlert-message").should("not.exist");
    });

    it("should display an alert when the 25 schedule limit is hit", () => {
        // Build a Schedule for Fall with SYSC 2006, ECOR 2050 & MATH 1005
        cy.get("#term-select").click().type("Fall");
        cy.get(".MuiAutocomplete-popper li").eq(0).click();
        cy.get("#course-select-0").click().type("SYSC 2006");
        cy.get(".MuiAutocomplete-popper li").eq(0).click();
        cy.get("#course-select-1").click().type("ECOR 2050");
        cy.get(".MuiAutocomplete-popper li").eq(0).click();
        cy.get("#course-select-2").click().type("MATH 1005");
        cy.get(".MuiAutocomplete-popper li").eq(0).click();
        cy.get("#build-button").click().wait(1000);

        cy.get(".MuiAlert-message").should("exist")
            .and("contain", "There are more than 25 results. Narrow your search to see more");
    });

    it("should display the term name in the title", () => {
        // Build a Schedule for Fall with SYSC 2006
        cy.get("#term-select").click().type("Fall");
        cy.get(".MuiAutocomplete-popper li").eq(0).click();
        cy.get("#course-select-0").click().type("SYSC 2006");
        cy.get(".MuiAutocomplete-popper li").eq(0).click();
        cy.get("#build-button").click().wait(1000);

        cy.get("h4").should("contain", "Fall");
    });

    it("should have the prev button disabled before clicking next", () => {
        // Build a Schedule for Fall with SYSC 2006
        cy.get("#term-select").click().type("Fall");
        cy.get(".MuiAutocomplete-popper li").eq(0).click();
        cy.get("#course-select-0").click().type("SYSC 2006");
        cy.get(".MuiAutocomplete-popper li").eq(0).click();
        cy.get("#build-button").click().wait(1000);

        cy.get("#prev-button").should("be.disabled");
        cy.get("#next-button").click();
        cy.get("#prev-button").should("be.enabled");
    });

    it("should have the next button enabled, then disabled on last schedule", () => {
        // Build a Schedule for Fall with SYSC 4810 A
        cy.get("#term-select").click().type("Fall");
        cy.get(".MuiAutocomplete-popper li").eq(0).click();
        cy.get("#course-select-0").click().type("SYSC 4810 A");
        cy.get(".MuiAutocomplete-popper li").eq(0).click();
        cy.get("#build-button").click().wait(1000);

        cy.get("#next-button").should("be.enabled");
        cy.get("#next-button").click().click().should("be.disabled");
    });

    it("should display a pop up when a event is clicked", () => {
        // Build a Schedule for Fall with SYSC 4810 A
        cy.get("#term-select").click().type("Fall");
        cy.get(".MuiAutocomplete-popper li").eq(0).click();
        cy.get("#course-select-0").click().type("SYSC 4810 A");
        cy.get(".MuiAutocomplete-popper li").eq(0).click();
        cy.get("#build-button").click().wait(1000);

        cy.get(".fc-event-main").eq(0).click();
        cy.get("#modal-title").should("exist");
        cy.get("#modal-description").should("exist");
    });

    it.only("should let you export the CRNs", () => {
        // Build a Schedule for Fall with SYSC 2006
        cy.get("#term-select").click().type("Fall");
        cy.get(".MuiAutocomplete-popper li").eq(0).click();
        cy.get("#course-select-0").click().type("SYSC 2006");
        cy.get(".MuiAutocomplete-popper li").eq(0).click();
        cy.get("#build-button").click().wait(1000);

        cy.get("#export-button").click().wait(1000);
        cy.get(".MuiAlert-message").should("exist")
            .and("contain", "CRNs copied to clipboard");
    });
});