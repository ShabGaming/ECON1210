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

def CalculateSubsidy(demand_eq: str, supply_eq: str, increase_Q=None, max_DWL=None, max_Expense=None):
    P, s = symbols('P s', real=True)
    
    def parse_equation(eq_str):
        lhs, rhs = preprocess_equation(eq_str)
        return sympify(rhs, {"P": P})
    
    D = parse_equation(demand_eq)  # Q_d(P)
    S = parse_equation(supply_eq)  # Q_s(P)
    
    # Find no-subsidy equilibrium:
    eq = Eq(D, S)
    sol = solve(eq, P)
    if not sol:
        if increase_Q is None and max_DWL is None and max_Expense is None:
            return ""
        return "No equilibrium found."

    P0 = sol[0]
    Q0 = D.subs(P, P0)

    # Conver P0 and Q0 to float
    P0_f = P0.evalf()
    Q0_f = Q0.evalf()
    # Set to 2 decimal places
    P0_f = round(P0_f, 2)
    Q0_f = round(Q0_f, 2)

    results = []
    results.append(f"Market Equilibrium Price: {P0_f} and Quantity: {Q0_f}")
    
    # Equilibrium with subsidy:
    def equilibrium_with_subsidy(subsidy):
        eq_sub = Eq(D.subs(P, P - subsidy), S)
        sol_sub = solve(eq_sub, P)
        if not sol_sub:
            return None, None
        P_star = sol_sub[0]
        Q_star = S.subs(P, P_star)
        return P_star, Q_star

    linear_market = is_linear(D, P) and is_linear(S, P)
    
    # If increase_Q is given:
    if increase_Q is not None:
        eq1 = Eq(D.subs(P, P - s), S)
        eq2 = Eq(S, Q0 + increase_Q)
        sol_increase = solve((eq1, eq2), (P, s), dict=True)
        if sol_increase:
            s_increase = sol_increase[0][s]

            # Convert to float at 2 decimal places
            s_increase_f = s_increase.evalf()
            s_increase_f = round(s_increase_f, 2)

            results.append(f"Subsidy to increase by {increase_Q}: {s_increase_f}")
        else:
            results.append(f"Subsidy to increase by {increase_Q}: No solution found")

    # If max_DWL is given and market is linear:
    if max_DWL is not None:
        if not linear_market:
            results.append("Subsidy to maximize DWL: Not applicable for non-linear market")
        else:
            # DWL = 0.5*(Q(s)-Q0)*s
            P_sub_sol = solve(Eq(D.subs(P, P - s), S), P)
            if P_sub_sol:
                P_sub_expr = P_sub_sol[0]
                Q_sub_expr = S.subs(P, P_sub_expr)
                dwl_eq = Eq(0.5*(Q_sub_expr - Q0)*s, max_DWL)
                sol_dwl = solve(dwl_eq, s)
                if sol_dwl:
                    s_candidates = [x for x in sol_dwl if x.is_real]
                    if s_candidates:
                        s_choice = None
                        for sc in s_candidates:
                            if sc > 0:
                                s_choice = sc
                                break
                        if s_choice is None:
                            s_choice = s_candidates[0]

                        # Convert to float at 2 decimal places
                        s_choice_f = s_choice.evalf()
                        s_choice_f = round(s_choice_f, 2)
    
                        results.append(f"Subsidy to maximize DWL: {s_choice_f}")
                    else:
                        results.append("Subsidy to maximize DWL: No real solution found")
                else:
                    results.append("Subsidy to maximize DWL: No solution found")
            else:
                results.append("Subsidy to maximize DWL: Could not solve equilibrium with subsidy")

    # If max_Expense is given:
    if max_Expense is not None:
        P_sub_sol = solve(Eq(D.subs(P, P - s), S), P)
        if P_sub_sol:
            P_sub_expr = P_sub_sol[0]
            Q_sub_expr = S.subs(P, P_sub_expr)
            expense_eq = Eq(s*Q_sub_expr, max_Expense)
            sol_expense = solve(expense_eq, s)
            if sol_expense:
                s_candidates = [x for x in sol_expense if x.is_real]
                if s_candidates:
                    s_choice = None
                    for sc in s_candidates:
                        if sc > 0:
                            s_choice = sc
                            break
                    if s_choice is None:
                        s_choice = s_candidates[0]

                    # Convert to float at 2 decimal places
                    s_choice_f = s_choice.evalf()
                    s_choice_f = round(s_choice_f, 2)
                    results.append(f"Subsidy to maximize Expense Budget: {s_choice_f}")
                else:
                    results.append("Subsidy to maximize Expense Budget: No real solution found")
            else:
                results.append("Subsidy to maximize Expense Budget: No solution found")
        else:
            results.append("Subsidy to maximize Expense Budget: Could not solve equilibrium with subsidy")

    # If all three are None, return empty
    if increase_Q is None and max_DWL is None and max_Expense is None:
        return ""

    return "\n".join(results)

# Test the code:
demand = "Q = 9400 - 1000P"
supply = "Q = 1000P - 3600"
res = CalculateSubsidy(demand, supply, max_Expense=49875)
print(res)