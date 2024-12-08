from sympy import symbols, sympify, solve, Eq
import re

def preprocess_equation(eq_str):
    eq_str = eq_str.replace(" ", "")
    lhs, rhs = eq_str.split('=')
    rhs = rhs.strip()
    
    # Insert '*' between a number and 'P'
    rhs = re.sub(r'(\d)(P)', r'\1*\2', rhs)
    # Insert '*' between number and '('
    rhs = re.sub(r'(\d)\(', r'\1*(', rhs)
    # Insert '*' if we have P(
    rhs = re.sub(r'(P)\(', r'\1*(', rhs)

    return lhs.strip(), rhs

def is_linear(expr, var):
    # Check linearity by examining the second derivative:
    return expr.diff(var, 2) == 0

def CalculateTax(demand_eq: str, supply_eq: str, decrease_Q=None, max_DWL=None, desired_Revenue=None):
    if demand_eq is None or supply_eq is None:
        return ""
    
    P, t = symbols('P t', real=True)
    
    def parse_equation(eq_str):
        lhs, rhs = preprocess_equation(eq_str)
        return sympify(rhs, {"P": P})
    
    D = parse_equation(demand_eq)  # Q_d(P)
    S = parse_equation(supply_eq)  # Q_s(P)
    
    # Find no-tax equilibrium:
    eq = Eq(D, S)
    sol = solve(eq, P)
    if not sol:
        if decrease_Q is None and max_DWL is None and desired_Revenue is None:
            return ""
        return "No equilibrium found."

    P0 = sol[0]
    Q0 = D.subs(P, P0)

    P0_f = P0.evalf()
    Q0_f = Q0.evalf()
    P0_f = round(P0_f, 2)
    Q0_f = round(Q0_f, 2)

    results = []
    results.append(f"Market Equilibrium Price: {P0_f} and Quantity: {Q0_f}")
    
    # Equilibrium with tax:
    # With a tax t on suppliers, they receive (P - t). Thus equilibrium: D(P) = S(P - t).
    def equilibrium_with_tax(tax):
        eq_tax = Eq(D, S.subs(P, P - tax))
        sol_tax = solve(eq_tax, P)
        if not sol_tax:
            return None, None
        P_star = sol_tax[0]
        Q_star = D.subs(P, P_star)  # or S(P_star - t), same at equilibrium
        return P_star, Q_star

    linear_market = is_linear(D, P) and is_linear(S, P)
    
    # If decrease_Q is given:
    # We want an equilibrium quantity Q* = Q0 - decrease_Q
    # Conditions:
    # 1) D(P) = S(P - t) at equilibrium
    # 2) S(P - t) = Q0 - decrease_Q (the new equilibrium quantity)
    if decrease_Q is not None:
        eq1 = Eq(D, S.subs(P, P - t))
        eq2 = Eq(S.subs(P, P - t), Q0 - decrease_Q)
        sol_decrease = solve((eq1, eq2), (P, t), dict=True)
        if sol_decrease:
            t_decrease = sol_decrease[0][t]
            t_decrease_f = t_decrease.evalf()
            t_decrease_f = round(t_decrease_f, 2)
            results.append(f"Tax to decrease Q by {decrease_Q}: {t_decrease_f}")
        else:
            results.append(f"Tax to decrease Q by {decrease_Q}: No solution found")

    # If max_DWL is given and market is linear:
    # DWL for a tax in a linear market: DWL = 0.5 * (Q0 - Q_tax) * t
    if max_DWL is not None:
        if not linear_market:
            results.append("Tax to maximize DWL: Not applicable for non-linear market")
        else:
            # Solve equilibrium with tax:
            # From D(P)=S(P-t), solve for P:
            P_tax_sol = solve(Eq(D, S.subs(P, P - t)), P)
            if P_tax_sol:
                P_tax_expr = P_tax_sol[0]
                Q_tax_expr = D.subs(P, P_tax_expr)

                # DWL = 0.5*(Q0 - Q_tax)*t
                dwl_eq = Eq(0.5*(Q0 - Q_tax_expr)*t, max_DWL)
                sol_dwl = solve(dwl_eq, t)
                if sol_dwl:
                    t_candidates = [x for x in sol_dwl if x.is_real]
                    if t_candidates:
                        # Choose a positive solution if possible
                        t_choice = None
                        for tc in t_candidates:
                            if tc > 0:
                                t_choice = tc
                                break
                        if t_choice is None:
                            t_choice = t_candidates[0]

                        t_choice_f = t_choice.evalf()
                        t_choice_f = round(t_choice_f, 2)
                        results.append(f"Tax to maximize DWL: {t_choice_f}")
                    else:
                        results.append("Tax to maximize DWL: No real solution found")
                else:
                    results.append("Tax to maximize DWL: No solution found")
            else:
                results.append("Tax to maximize DWL: Could not solve equilibrium with tax")

    # If desired_Revenue is given:
    # Tax revenue = t * Q_tax
    # Q_tax = from equilibrium: Q_tax = D(P_tax) = S(P_tax - t)
    if desired_Revenue is not None:
        P_tax_sol = solve(Eq(D, S.subs(P, P - t)), P)
        if P_tax_sol:
            P_tax_expr = P_tax_sol[0]
            Q_tax_expr = D.subs(P, P_tax_expr)
            revenue_eq = Eq(t*Q_tax_expr, desired_Revenue)
            sol_revenue = solve(revenue_eq, t)
            if sol_revenue:
                t_candidates = [x for x in sol_revenue if x.is_real]
                if t_candidates:
                    # Choose a positive solution if possible
                    t_choice = None
                    for tc in t_candidates:
                        if tc > 0:
                            t_choice = tc
                            break
                    if t_choice is None:
                        t_choice = t_candidates[0]

                    t_choice_f = t_choice.evalf()
                    t_choice_f = round(t_choice_f, 2)
                    results.append(f"Tax to maximize Revenue: {t_choice_f}")
                else:
                    results.append("Tax to maximize Revenue: No real solution found")
            else:
                results.append("Tax to maximize Revenue: No solution found")
        else:
            results.append("Tax to maximize Revenue: Could not solve equilibrium with tax")

    # If all three are None, return empty
    if decrease_Q is None and max_DWL is None and desired_Revenue is None:
        return ""

    return "\n".join(results)

CalculateTax(arg1, arg2, arg3, arg4, arg5)