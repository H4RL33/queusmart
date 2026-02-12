import datetime

def calculate_priority_score(ticket_row):
    """
    Works out how urgent a request is by assigning it a score based on rules.
    
    The rules we use are:
    - Very high urgency adds 50 points.
    - High urgency adds 30 points.
    - Requests that have been waiting for more than a day get 1 extra point for every hour past that first day.
    - Housing-related requests get 10 extra points.
    - If the customer is marked as 'vulnerable' (needing extra care), we add 15 points.
    """
    score = 0
    
    # 1. We check the urgency level set by staff.
    urgency = ticket_row.get('urgency', 'Low')
    if urgency == 'Critical':
        score += 50
    elif urgency == 'High':
        score += 30
        
    # 2. We give extra priority to Housing issues.
    if ticket_row.get('category') == 'Housing':
        score += 10
        
    # 3. We give extra priority to customers who need more support.
    if ticket_row.get('is_vulnerable', 0):
        score += 15
        
    # 4. We give extra priority to older requests that have been waiting a long time.
    created_at_str = ticket_row.get('created_at')
    if created_at_str:
        try:
            created_at = datetime.datetime.fromisoformat(created_at_str)
            now = datetime.datetime.now()
            diff = now - created_at
            hours_old = diff.total_seconds() / 3600
            
            if hours_old > 24:
                # We add 1 point for every hour the request has been waiting past its first 24 hours.
                score += int(hours_old - 24)
        except ValueError:
            pass # If the date is missing or incorrect, we just don't add any extra points for age.
            
    return score

def sort_tickets_by_priority(tickets_list):
    """
    Organizes a list of requests so that the most urgent ones (the ones with the highest scores) appear at the very top.
    """
    for ticket in tickets_list:
        # We first calculate the score for each individual request.
        ticket['priority_score'] = calculate_priority_score(ticket)
        
    # We then sort the list from highest score to lowest.
    return sorted(tickets_list, key=lambda x: x['priority_score'], reverse=True)
