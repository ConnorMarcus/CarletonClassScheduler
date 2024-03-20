describe('App tests', () => {
  it('Root div should exist', () => {
    cy.visit('/');
    cy.get('#root').should('exist');
  });
});