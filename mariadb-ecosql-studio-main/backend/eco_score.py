def calculate_eco_score(explain_output) -> float:
   total_rows = sum(row[8] for row in explain_output if row[8])
   if total_rows < 1000:
       return "Low"
   elif total_rows < 10000:
       return "Medium"
   else:
       return "High"