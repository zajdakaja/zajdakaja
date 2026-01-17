describe("Mobile dashboard flow", () => {
  it("logs in and shows dashboard", () => {
    cy.visit("/");
    cy.contains("Zaloguj się");
    cy.get("input").first().clear().type("demo");
    cy.get("input[type=\"password\"]").clear().type("demo123");
    cy.contains("Zaloguj się").click();
    cy.contains("Dashboard");
    cy.contains("Lista zadań");
  });
});
