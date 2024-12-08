import sympy as sp

def Subsidy(demand_eq, supply_eq, subsidy, To_Whom='C'):
    # Example input: demand_eq = "Q = 3040 - 25P"
    #                supply_eq = "Q = 1.8 + 9P"
    # We will parse these equations into sympy expressions.
    # We assume the format "Q =" is always at the start and solve for Q as a function of P.
    
    # Extract the right-hand side of the equations
    demand_rhs = demand_eq.split('=')[1].strip()
    supply_rhs = supply_eq.split('=')[1].strip()
    
    # We'll define a variable P for price and Q for quantity
    P = sp.Symbol('P', real=True)
    # We will create expressions for Qd(P) and Qs(P).
    
    # Convert something like "3040 - 25P" or "20 - 23(P^2)" to a pythonic expression:
    # Replace 'P' with '*P' where appropriate and handle powers:
    # A safe way: Replace occurrences of P with (P), then replace (P^2) with (P**2)
    # We'll do a more robust parse:
    def parse_equation(rhs):
        expr = rhs.replace('^', '**')
        # Ensure multiplication is explicit. For example "25P" -> "25*P"
        # We'll insert a '*' before 'P' if there's a digit or a closing parenthesis before it.
        # A quick approach:
        expr = expr.replace('(', '*(') # This might overinsert '*'
        # We'll revert the first char if it is '*(':
        if expr.startswith('*('):
            expr = expr[1:]
        # A more robust approach:
        # We'll handle replacements carefully
        # Actually, let's do a small manual parse:
        # We'll insert '*' before P if needed
        expr_modified = ""
        for i, ch in enumerate(expr):
            if ch == 'P':
                # check previous character
                if i > 0 and (expr[i-1].isdigit() or expr[i-1] == ')' or expr[i-1] == 'P'):
                    expr_modified += '*' + ch
                else:
                    expr_modified += ch
            else:
                expr_modified += ch
        expr = expr_modified
        # Now convert to sympy
        return sp.sympify(expr, {'P':P})
    
    Qd_expr = parse_equation(demand_rhs)
    Qs_expr = parse_equation(supply_rhs)
    
    # Find initial equilibrium by solving Qd(P) = Qs(P)
    eq_solution = sp.solve(sp.Eq(Qd_expr, Qs_expr), P)
    if not eq_solution:
        return "No equilibrium solution found."
    # If multiple solutions, take the one that makes economic sense (positive Q and P)
    # We'll pick the first positive solution if exists
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
        # If no positive solution found, just take the first solution
        P0 = eq_solution[0]
    Q0 = Qd_expr.subs(P, P0)
    
    # Now apply the subsidy
    # If subsidy to consumers: Qd depends on (P - subsidy), supply on P.
    # Condition: Qd(P_s - S) = Qs(P_s)  -> Solve for P_s
    # If subsidy to producers: Qs depends on (P_b + S), Qd on P_b.
    # Condition: Qd(P_b) = Qs(P_b + S) -> Solve for P_b
    
    if To_Whom == 'C':  # Consumer subsidy
        # Let Ps = price received by sellers, then buyers pay Pb = Ps - S
        # Solve Qd(Ps - S) = Qs(Ps)
        Ps = sp.Symbol('Ps', real=True)
        eq_subsidy = sp.Eq(Qd_expr.subs(P, Ps - subsidy), Qs_expr.subs(P, Ps))
        sol_subsidy = sp.solve(eq_subsidy, Ps)
        # Choose a valid solution
        Ps_new = None
        for candidate in sol_subsidy:
            Q_candidate = Qd_expr.subs(P, candidate - subsidy)
            if candidate > 0 and Q_candidate > 0:
                Ps_new = candidate
                break
        if Ps_new is None:
            Ps_new = sol_subsidy[0]
        Pb_new = Ps_new - subsidy
        Q_new = Qd_expr.subs(P, Pb_new)
        
    elif To_Whom == 'P':  # Producer subsidy
        # Let Pb = price paid by buyers, Ps = price received by sellers = Pb + S
        # Solve Qd(Pb) = Qs(Pb + S)
        Pb = sp.Symbol('Pb', real=True)
        eq_subsidy = sp.Eq(Qd_expr.subs(P, Pb), Qs_expr.subs(P, Pb + subsidy))
        sol_subsidy = sp.solve(eq_subsidy, Pb)
        Pb_new = None
        for candidate in sol_subsidy:
            Q_candidate = Qd_expr.subs(P, candidate)
            if candidate > 0 and Q_candidate > 0:
                Pb_new = candidate
                break
        if Pb_new is None:
            Pb_new = sol_subsidy[0]
        Ps_new = Pb_new + subsidy
        Q_new = Qd_expr.subs(P, Pb_new)
        
    else:
        # If no "To_Whom" specified, assume consumer subsidy as default
        # Same as To_Whom == 'C'
        Ps = sp.Symbol('Ps', real=True)
        eq_subsidy = sp.Eq(Qd_expr.subs(P, Ps - subsidy), Qs_expr.subs(P, Ps))
        sol_subsidy = sp.solve(eq_subsidy, Ps)
        Ps_new = None
        for candidate in sol_subsidy:
            Q_candidate = Qd_expr.subs(P, candidate - subsidy)
            if candidate > 0 and Q_candidate > 0:
                Ps_new = candidate
                break
        if Ps_new is None:
            Ps_new = sol_subsidy[0]
        Pb_new = Ps_new - subsidy
        Q_new = Qd_expr.subs(P, Pb_new)
        To_Whom = 'C'
    
    # Identify Pb_new and Ps_new depending on the scenario:
    if To_Whom == 'C':
        buyer_price_after = Pb_new
        seller_price_after = Ps_new
    else:
        buyer_price_after = Pb_new
        seller_price_after = Ps_new

    buyer_paying_less_by = P0 - buyer_price_after
    seller_receiving_more_by = seller_price_after - P0
    
    # Government cost:
    gov_cost = subsidy * Q_new  # In the same units (thousand dollars if Q in thousands)
    
    # To compute DWL, we need CS and PS before and after.
    # We'll define a helper to find inverse functions and integrate.
    
    # Inverse demand and supply: We have Q = f(P). We want P as a function of Q.
    Q = sp.Symbol('Q', real=True)
    
    # Solve for P in terms of Q for demand: Q = Qd_expr -> P = Pd(Q)
    Pd_solutions = sp.solve(sp.Eq(Q, Qd_expr), P)
    if not Pd_solutions:
        return "Could not invert demand function."
    Pd_func = None
    for sol in Pd_solutions:
        # Choose a real solution
        if sol.is_real or sol.is_real is None:
            Pd_func = sol
            break
    if Pd_func is None:
        Pd_func = Pd_solutions[0]
    
    # Solve for supply inverse: Q = Qs_expr -> P = Ps(Q)
    Ps_solutions = sp.solve(sp.Eq(Q, Qs_expr), P)
    if not Ps_solutions:
        return "Could not invert supply function."
    Ps_func = None
    for sol in Ps_solutions:
        if sol.is_real or sol.is_real is None:
            Ps_func = sol
            break
    if Ps_func is None:
        Ps_func = Ps_solutions[0]
    
    # Consumer Surplus (CS) = ∫0 to Q0 Pd(Q') dQ' - P0*Q0
    # Producer Surplus (PS) = P0*Q0 - ∫0 to Q0 Ps(Q') dQ'
    
    # Before subsidy:
    CS_before = sp.integrate(Pd_func, (Q, 0, Q0)) - P0*Q0
    PS_before = P0*Q0 - sp.integrate(Ps_func, (Q, 0, Q0))
    TS_before = CS_before + PS_before  # No gov
    
    # After subsidy:
    # For inverse demand after consumer subsidy: the consumer price is Pb (if to consumers)
    # Actually, the definition of CS and PS does not change. We still use original Pd(Q) and Ps(Q).
    # Just the equilibrium changes.
    # After subsidy to consumers: 
    #    Equilibrium Q_new.
    #    Buyers pay Pb_new, sellers receive Ps_new.
    # CS_after = ∫0 to Q_new Pd(Q') dQ' - Pb_new*Q_new
    # PS_after = Ps_new*Q_new - ∫0 to Q_new Ps(Q') dQ'
    
    # After subsidy to producers:
    #   The formulas are the same. It's always:
    #   CS = ∫0 to Q_new Pd(Q') dQ' - Price buyers pay * Q_new
    #   PS = Price sellers get * Q_new - ∫0 to Q_new Ps(Q') dQ'
    
    CS_after = sp.integrate(Pd_func, (Q, 0, Q_new)) - buyer_price_after*Q_new
    PS_after = seller_price_after*Q_new - sp.integrate(Ps_func, (Q, 0, Q_new))
    TS_after = CS_after + PS_after
    
    # The government spends gov_cost, so Net Social Surplus after subsidy:
    # NSS_after = CS_after + PS_after - gov_cost
    # DWL = TS_before - NSS_after = TS_before - (CS_after + PS_after - gov_cost)
    DWL = TS_before - (TS_after - gov_cost)
    
    # Build the output string
    # Required structure:
    # - Market equilibrium price and Quantity
    # - After subsidy buyers pay 'x' and sellers make 'y'
    # - Cost of Subsidy to Gov: 'x', DWL: 'y'
    # (Optional if To_Whom is given):
    # - After Subsidy Consumer Surplus: , Producer Surplus:
    
    result = []
    result.append(f"Market equilibrium price: {float(P0):.2f}, Quantity: {float(Q0):.2f}")
    result.append(f"After subsidy buyers pay: {float(buyer_price_after):.2f} (less by {float(buyer_paying_less_by):.2f}) and sellers make: {float(seller_price_after):.2f} (more by {float(seller_receiving_more_by):.2f})")
    result.append(f"Cost of Subsidy to Gov: {float(gov_cost):.2f}, DWL: {float(DWL):.2f}")
    
    if To_Whom is not None:
        result.append(f"After Subsidy Consumer Surplus: {float(CS_after):.2f}, Producer Surplus: {float(PS_after):.2f}")
    
    return "\n".join(result)

Subsidy(arg1, arg2, arg3, arg4)