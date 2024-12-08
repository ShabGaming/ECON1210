import sympy as sp

def Tax(demand_eq, supply_eq, tax, On_Whom='P'):
    if not demand_eq or not supply_eq:
        return ""

    # Example input: demand_eq = "Q = 3040 - 25P"
    #                supply_eq = "Q = 1.8 + 9P"
    # We parse these equations into sympy expressions.

    # Extract the right-hand side of the equations
    demand_rhs = demand_eq.split('=')[1].strip()
    supply_rhs = supply_eq.split('=')[1].strip()
    
    P = sp.Symbol('P', real=True)
    
    def parse_equation(rhs):
        expr = rhs.replace('^', '**')
        # Insert '*' before P if needed
        expr_modified = ""
        for i, ch in enumerate(expr):
            if ch == 'P':
                if i > 0 and (expr[i-1].isdigit() or expr[i-1] == ')' or expr[i-1] == 'P'):
                    expr_modified += '*' + ch
                else:
                    expr_modified += ch
            else:
                expr_modified += ch
        expr = expr_modified
        return sp.sympify(expr, {'P':P})
    
    Qd_expr = parse_equation(demand_rhs)
    Qs_expr = parse_equation(supply_rhs)
    
    # Find initial equilibrium by solving Qd(P) = Qs(P)
    eq_solution = sp.solve(sp.Eq(Qd_expr, Qs_expr), P)
    if not eq_solution:
        return "No equilibrium solution found."
    P0_candidates = [sol for sol in eq_solution if sol.is_real]
    if not P0_candidates:
        return "No real equilibrium solution."
    P0 = None
    for candidate in P0_candidates:
        Q_candidate = Qd_expr.subs(P, candidate)
        if candidate > 0 and Q_candidate > 0:
            P0 = candidate
            break
    if P0 is None:
        P0 = eq_solution[0]
    Q0 = Qd_expr.subs(P, P0)
    
    # Apply the tax
    # If tax on producers (default): Qd(Pb) = Qs(Pb - tax)
    # If tax on consumers: Qd(Ps + tax) = Qs(Ps)
    
    if On_Whom == 'P':  # Producer tax
        Pb = sp.Symbol('Pb', real=True)
        eq_tax = sp.Eq(Qd_expr.subs(P, Pb), Qs_expr.subs(P, Pb - tax))
        sol_tax = sp.solve(eq_tax, Pb)
        Pb_new = None
        for candidate in sol_tax:
            Q_candidate = Qd_expr.subs(P, candidate)
            if candidate > 0 and Q_candidate > 0:
                Pb_new = candidate
                break
        if Pb_new is None:
            Pb_new = sol_tax[0]
        Ps_new = Pb_new - tax
        Q_new = Qd_expr.subs(P, Pb_new)
        
    elif On_Whom == 'C':  # Consumer tax
        Ps = sp.Symbol('Ps', real=True)
        eq_tax = sp.Eq(Qd_expr.subs(P, Ps + tax), Qs_expr.subs(P, Ps))
        sol_tax = sp.solve(eq_tax, Ps)
        Ps_new = None
        for candidate in sol_tax:
            Q_candidate = Qd_expr.subs(P, candidate + tax)
            if candidate > 0 and Q_candidate > 0:
                Ps_new = candidate
                break
        if Ps_new is None:
            Ps_new = sol_tax[0]
        Pb_new = Ps_new + tax
        Q_new = Qd_expr.subs(P, Pb_new)
    else:
        # Default to producer tax if invalid input
        On_Whom = 'P'
        Pb = sp.Symbol('Pb', real=True)
        eq_tax = sp.Eq(Qd_expr.subs(P, Pb), Qs_expr.subs(P, Pb - tax))
        sol_tax = sp.solve(eq_tax, Pb)
        Pb_new = None
        for candidate in sol_tax:
            Q_candidate = Qd_expr.subs(P, candidate)
            if candidate > 0 and Q_candidate > 0:
                Pb_new = candidate
                break
        if Pb_new is None:
            Pb_new = sol_tax[0]
        Ps_new = Pb_new - tax
        Q_new = Qd_expr.subs(P, Pb_new)
    
    # Identify final buyer and seller prices
    if On_Whom == 'P':
        buyer_price_after = Pb_new
        seller_price_after = Ps_new
    else:
        buyer_price_after = Pb_new
        seller_price_after = Ps_new
    
    # Changes in prices due to the tax
    buyer_paying_more_by = buyer_price_after - P0
    seller_receiving_less_by = P0 - seller_price_after
    
    # Tax revenue
    tax_revenue = tax * Q_new
    
    # Calculate CS, PS, and DWL
    Q = sp.Symbol('Q', real=True)
    
    # Inverse demand: solve Q = Qd_expr for P
    Pd_solutions = sp.solve(sp.Eq(Q, Qd_expr), P)
    Pd_func = None
    for sol in Pd_solutions:
        if sol.is_real or sol.is_real is None:
            Pd_func = sol
            break
    if Pd_func is None:
        Pd_func = Pd_solutions[0]
    
    # Inverse supply: solve Q = Qs_expr for P
    Ps_solutions = sp.solve(sp.Eq(Q, Qs_expr), P)
    Ps_func = None
    for sol in Ps_solutions:
        if sol.is_real or sol.is_real is None:
            Ps_func = sol
            break
    if Ps_func is None:
        Ps_func = Ps_solutions[0]
    
    # Before tax:
    CS_before = sp.integrate(Pd_func, (Q, 0, Q0)) - P0*Q0
    PS_before = P0*Q0 - sp.integrate(Ps_func, (Q, 0, Q0))
    TS_before = CS_before + PS_before  # No government revenue before tax
    
    # After tax:
    CS_after = sp.integrate(Pd_func, (Q, 0, Q_new)) - buyer_price_after*Q_new
    PS_after = seller_price_after*Q_new - sp.integrate(Ps_func, (Q, 0, Q_new))
    # Total surplus after tax includes government revenue:
    TS_after = CS_after + PS_after + tax_revenue
    
    # Deadweight loss = TS_before - TS_after
    DWL = TS_before - TS_after
    
    # Build the output
    result = []
    result.append(f"Market equilibrium price: {float(P0):.2f}, Quantity: {float(Q0):.2f}")
    result.append(f"After tax buyers pay: {float(buyer_price_after):.2f} (more by {float(buyer_paying_more_by):.2f})")
    result.append(f"After tax sellers make: {float(seller_price_after):.2f} (less by {float(seller_receiving_less_by):.2f})")
    result.append(f"Tax Revenue: {float(tax_revenue):.2f}, DWL: {float(DWL):.2f}")
    result.append(f"After Tax Consumer Surplus: {float(CS_after):.2f}, Producer Surplus: {float(PS_after):.2f}")
    
    return "\n".join(result)

Tax(arg1, arg2, arg3, arg4)