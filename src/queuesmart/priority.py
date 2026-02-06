import datetime

def calculate_priority_score(ticket_row):
    """
    Calculates the priority score for a ticket based on business rules.
    
    Rules:
    - Base: Critical (+50), High (+30)
    - Aging: +1 per hour after 24 hours
    - Category: Housing (+10)
    - Vulnerability: Customer is vulnerable (+15)
    """
    score = 0
    
    # 1. Base Score
    urgency = ticket_row.get('urgency', 'Low')
    if urgency == 'Critical':
        score += 50
    elif urgency == 'High':
        score += 30
        
    # 2. Category Bonus
    if ticket_row.get('category') == 'Housing':
        score += 10
        
    # 3. Vulnerability Bonus
    # Note: 'is_vulnerable' should be part of ticket_row (joined from customers)
    if ticket_row.get('is_vulnerable', 0):
        score += 15
        
    # 4. Aging Bonus
    created_at_str = ticket_row.get('created_at')
    if created_at_str:
        try:
            created_at = datetime.datetime.fromisoformat(created_at_str)
            now = datetime.datetime.now()
            diff = now - created_at
            hours_old = diff.total_seconds() / 3600
            
            if hours_old > 24:
                # 1 point for every hour past 24
                score += int(hours_old - 24)
        except ValueError:
            pass # Handle invalid date gracefully (no bonus)
            
    return score

def sort_tickets_by_priority(tickets_list):
    """
    Sorts a list of tickets by their calculated priority score (Descending).
    Also attaches the 'priority_score' to each ticket dictionary.
    """
    for ticket in tickets_list:
        ticket['priority_score'] = calculate_priority_score(ticket)
        
    # Sort descending
    return sorted(tickets_list, key=lambda x: x['priority_score'], reverse=True)
