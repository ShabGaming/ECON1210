import sympy as sp

def PriceGuarantee(demand_eq, supply_eq, promise_to_buy_at, storage_cost):
    # demand_eq and supply_eq are strings like "Q = 660 - 6.6P" or "Q = 59(P) - 3(P^2)"
    # promise_to_buy_at is the guaranteed price (P_g)
    # storage_cost is the storage cost per unit

    if demand_eq is None or supply_eq is None:
        return ""

    if storage_cost is None:
        storage_cost = 0

    P = sp.Symbol('P', real=True)
    Q = sp.Symbol('Q', real=True)

    def parse_equation(eq_str):
        # eq_str is something like "Q = 3040 - 25P"
        # Extract the right side
        rhs = eq_str.split('=')[1].strip()
        # Replace '^' with '**' for power
        rhs = rhs.replace('^', '**')
        # Insert '*' before P where needed
        expr_modified = ""
        for i, ch in enumerate(rhs):
            if ch == 'P':
                # If previous char is digit or ')' or 'P', insert '*'
                if i > 0 and (rhs[i-1].isdigit() or rhs[i-1] == ')' or rhs[i-1] == 'P'):
                    expr_modified += '*' + ch
                else:
                    expr_modified += ch
            else:
                expr_modified += ch
        rhs_expr = sp.sympify(expr_modified, {'P':P})
        return rhs_expr

    Qd_expr = parse_equation(demand_eq)
    Qs_expr = parse_equation(supply_eq)

    # Find equilibrium: solve Qd(P) = Qs(P)
    eq_solution = sp.solve(sp.Eq(Qd_expr, Qs_expr), P)
    # eq_solution might be a list of solutions. Choose a suitable one (positive)
    P_eq_candidates = [sol for sol in eq_solution if sol.is_real and sol > 0]
    if not P_eq_candidates:
        # fallback to any real solution if no positive found
        P_eq_candidates = [sol for sol in eq_solution if sol.is_real]
    if not P_eq_candidates:
        raise ValueError("No suitable equilibrium price found.")
    P_eq = P_eq_candidates[0]

    Q_eq = Qd_expr.subs(P, P_eq)

    # Now consider the price guarantee P_g
    P_g = promise_to_buy_at
    Q_sg = Qs_expr.subs(P, P_g)
    Q_dg = Qd_expr.subs(P, P_g)

    # Government needs to buy:
    Q_gov = Q_sg - Q_dg if Q_sg > Q_dg else 0

    # To find inverse functions for surplus calculation:
    # Invert demand: Q = D(P) -> P = D^{-1}(Q)
    inv_demand_solutions = sp.solve(sp.Eq(Q, Qd_expr), P)
    # Choose a suitable inverse that is a proper increasing function of Q
    # Typically, demand is downward sloping, so we pick the appropriate solution.
    # If there's more than one solution, pick the real and valid branch.
    inv_demand = None
    for sol in inv_demand_solutions:
        # Check if valid over relevant range Q=0 to Q_dg
        if sol.is_real:
            inv_demand = sol
            break
    if inv_demand is None:
        raise ValueError("Could not invert demand function.")

    # Invert supply: Q = S(P) -> P = S^{-1}(Q)
    inv_supply_solutions = sp.solve(sp.Eq(Q, Qs_expr), P)
    inv_supply = None
    for sol in inv_supply_solutions:
        if sol.is_real:
            inv_supply = sol
            break
    if inv_supply is None:
        raise ValueError("Could not invert supply function.")

    # Producer Surplus at price guarantee:
    # PS = ∫0 to Q_sg [P_g - P_s(Q)] dQ
    # We'll integrate symbolically:
    PS_expr = sp.integrate((P_g - inv_supply), (Q, 0, Q_sg))

    # Consumer Surplus at price guarantee:
    # CS = ∫0 to Q_dg P_d(Q) dQ - P_g * Q_dg
    CS_expr = sp.integrate(inv_demand, (Q, 0, Q_dg)) - P_g * Q_dg

    # Total government cost:
    gov_cost = Q_gov * (P_g + storage_cost)

    # Format the output string
    # Round values for neatness (optional)
    return (f"Market Equilibrium Price: {float(P_eq):.2f}, and Quantity: {float(Q_eq):.2f}\n"
            f"Government needs to buy: {float(Q_gov):.2f}\n"
            f"Producer Surplus: {float(PS_expr):.2f}, and Consumer Surplus: {float(CS_expr):.2f}\n"
            f"total cost to Gov (including storage cost): {float(gov_cost):.2f}")

PriceGuarantee(arg1, arg2, arg3, arg4)
