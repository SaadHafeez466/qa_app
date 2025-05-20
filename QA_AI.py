import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import openai
import csv
import os
import json
from datetime import datetime

class TestCaseGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CureMD Test Case Generator")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f2f5")
        
        # Set icon (if available)
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
            
        # Initialize variables
        self.api_key = tk.StringVar()
        self.user_story = tk.StringVar()
        self.output_file = tk.StringVar(value="test_cases_output.csv")
        self.selected_categories = []
        self.categories = [
            "Functional test cases",
            "Acceptance test cases",
            "Negative test cases",
            "Edge cases",
            "Error and validation test cases",
            "Performance/load test cases",
            "Security-related test cases",
            "Cross-platform test cases"
        ]
        
        # Try to load saved API key
        self.load_api_key()
        
        # Create the UI
        self.create_ui()
        
    def load_api_key(self):
        """Load API key from config file if it exists"""
        try:
            if os.path.exists("config.json"):
                with open("config.json", "r") as f:
                    config = json.load(f)
                    if "api_key" in config:
                        self.api_key.set(config["api_key"])
        except Exception as e:
            print(f"Error loading API key: {e}")
    
    def save_api_key(self):
        """Save API key to config file"""
        try:
            with open("config.json", "w") as f:
                json.dump({"api_key": self.api_key.get()}, f)
        except Exception as e:
            print(f"Error saving API key: {e}")
    
    def create_ui(self):
        """Create the application UI"""
        # Main frame
        main_frame = tk.Frame(self.root, bg="#f0f2f5")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_frame = tk.Frame(main_frame, bg="#f0f2f5")
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            title_frame, 
            text="CureMD", 
            font=("Arial", 24, "bold"), 
            fg="#1a73e8", 
            bg="#f0f2f5"
        ).pack(side=tk.LEFT)
        
        tk.Label(
            title_frame, 
            text="Application Improvements", 
            font=("Arial", 24), 
            fg="#202124", 
            bg="#f0f2f5"
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # Settings Section
        settings_frame = tk.LabelFrame(main_frame, text="Settings", bg="#ffffff", padx=15, pady=15)
        settings_frame.pack(fill=tk.X, pady=(0, 15))
        
        # API Key
        api_frame = tk.Frame(settings_frame, bg="#ffffff")
        api_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(api_frame, text="OpenAI API Key:", bg="#ffffff").pack(side=tk.LEFT)
        
        api_entry = tk.Entry(api_frame, textvariable=self.api_key, width=50, show="•")
        api_entry.pack(side=tk.LEFT, padx=(10, 10))
        
        # tk.Button(
        #     api_frame, 
        #     text="Show/Hide", 
        #     command=lambda: api_entry.config(show="" if api_entry.cget("show") else "•"),
        #     bg="#e0e0e0"
        # ).pack(side=tk.LEFT)
        
        # tk.Button(
        #     api_frame, 
        #     text="Save Key", 
        #     command=self.save_api_key,
        #     bg="#e0e0e0"
        # ).pack(side=tk.LEFT, padx=(10, 0))
        
        # Output file
        file_frame = tk.Frame(settings_frame, bg="#ffffff")
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
   #     tk.Label(file_frame, text="Output File(Leave it as it is):", bg="#ffffff").pack(side=tk.LEFT)
        
   #     tk.Entry(file_frame, textvariable=self.output_file, width=50).pack(side=tk.LEFT, padx=(20, 10))
        
   #     tk.Button(
   #         file_frame, 
   #         text="Browse...", 
  #          command=self.browse_output_file,
   #         bg="#e0e0e0"
  #      ).pack(side=tk.LEFT)
        
        # Categories
        categories_frame = tk.LabelFrame(main_frame, text="Test Case Categories", bg="#ffffff", padx=15, pady=15)
        categories_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Create checkboxes in a grid layout
        self.category_vars = []
        category_frame = tk.Frame(categories_frame, bg="#ffffff")
        category_frame.pack(fill=tk.X)
        
        col, row = 0, 0
        for category in self.categories:
            var = tk.BooleanVar(value=True)
            self.category_vars.append(var)
            
            cb = tk.Checkbutton(
                category_frame, 
                text=category, 
                variable=var, 
                bg="#ffffff",
                anchor="w",
                width=25
            )
            cb.grid(row=row, column=col, sticky="w", pady=2)
            
            col += 1
            if col > 1:
                col = 0
                row += 1
        
        # Select/Deselect All buttons
        button_frame = tk.Frame(categories_frame, bg="#ffffff")
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Button(
            button_frame, 
            text="Select All", 
            command=lambda: self.toggle_all_categories(True),
            bg="#e0e0e0"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            button_frame, 
            text="Deselect All", 
            command=lambda: self.toggle_all_categories(False),
            bg="#e0e0e0"
        ).pack(side=tk.LEFT)
        
        # User Story Input
        story_frame = tk.LabelFrame(main_frame, text="User Story", bg="#ffffff", padx=15, pady=15)
        story_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.story_text = scrolledtext.ScrolledText(story_frame, wrap=tk.WORD, height=10, width=80)
        self.story_text.pack(fill=tk.BOTH, expand=True)
        self.story_text.bind("<KeyRelease>", self.update_char_count)
        
        # Character count
        self.char_count_var = tk.StringVar(value="5000 characters remaining")
        char_count_label = tk.Label(
            story_frame, 
            textvariable=self.char_count_var, 
            anchor="e", 
            fg="#666666",
            bg="#ffffff"
        )
        char_count_label.pack(fill=tk.X)
        
        # Results section
        results_frame = tk.LabelFrame(main_frame, text="Results", bg="#ffffff", padx=15, pady=15)
        results_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.progress = ttk.Progressbar(results_frame, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        self.status_var = tk.StringVar(value="Ready")
        status_label = tk.Label(results_frame, textvariable=self.status_var, bg="#ffffff")
        status_label.pack(fill=tk.X)
        
        # Buttons frame
        button_frame = tk.Frame(main_frame, bg="#f0f2f5")
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Generate button
        generate_button = tk.Button(
            button_frame,
            text="Generate Test Cases",
            command=self.start_generation,
            bg="#1a73e8",
            fg="white",
            font=("Arial", 14, "bold"),
            pady=10,
            width=20
        )
        generate_button.pack(side=tk.LEFT, padx=(0, 10), ipady=5)
        
        # Exit button
        exit_button = tk.Button(
            button_frame,
            text="Exit",
            command=self.root.destroy,
            bg="#e0e0e0",
            font=("Arial", 14),
            pady=10,
            width=10
        )
        exit_button.pack(side=tk.LEFT, ipady=5)
    
    def toggle_all_categories(self, state):
        """Select or deselect all categories"""
        for var in self.category_vars:
            var.set(state)
    
    def update_char_count(self, event=None):
        """Update the character count as the user types"""
        remaining = 5000 - len(self.story_text.get("1.0", tk.END + "-1c"))
        self.char_count_var.set(f"{remaining} characters remaining")
    
    def browse_output_file(self):
        """Open a file dialog to select output file location"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.output_file.set(filename)
    
    def start_generation(self):
        """Start the test case generation process"""
        # Validate inputs
        if not self.api_key.get().strip():
            messagebox.showerror("Error", "Please enter your OpenAI API key")
            return
        
        user_story = self.story_text.get("1.0", tk.END + "-1c").strip()
        if not user_story:
            messagebox.showerror("Error", "Please enter a user story")
            return
        
        selected_categories = []
        for i, var in enumerate(self.category_vars):
            if var.get():
                selected_categories.append(self.categories[i])
        
        if not selected_categories:
            messagebox.showerror("Error", "Please select at least one test case category")
            return
        
        # Set OpenAI API key
        openai.api_key = self.api_key.get().strip()
        
        # Disable UI elements during generation
        self.toggle_ui_state(False)
        
        # Start generation in separate thread
        threading.Thread(target=self.generate_test_cases, args=(user_story, selected_categories), daemon=True).start()
    
    def toggle_ui_state(self, enabled):
        """Enable/disable UI elements during processing"""
        state = "normal" if enabled else "disabled"
        for widget in self.root.winfo_children():
            self.set_widget_state(widget, state)
    
    def set_widget_state(self, widget, state):
        """Recursively set widget state"""
        if widget.winfo_children():
            for child in widget.winfo_children():
                self.set_widget_state(child, state)
        else:
            if hasattr(widget, "state") and callable(getattr(widget, "state")):
                if state == "normal":
                    widget.state(["!disabled"])
                else:
                    widget.state(["disabled"])
            elif hasattr(widget, "configure") and callable(getattr(widget, "configure")):
                try:
                    widget.configure(state=state)
                except:
                    pass
    
    def generate_test_cases(self, user_story, categories):
        """Generate test cases based on user input"""
        test_cases = []
        num_categories = len(categories)
        
        try:
            for i, category in enumerate(categories):
                # Update progress bar
                progress_value = int((i / num_categories) * 100)
                self.root.after(0, lambda v=progress_value: self.progress.configure(value=v))
                self.root.after(0, lambda c=category: self.status_var.set(f"Generating {c}..."))
                
                # Generate test cases
                response_text = self.get_test_cases(category, user_story)
                
                # Parse the response text
                new_cases = self.parse_response(response_text, category)
                test_cases.extend(new_cases)
            
            # Save results to CSV
            self.save_to_csv(test_cases)
            
            # Show success message
            self.root.after(0, lambda n=len(test_cases): 
                messagebox.showinfo("Success", f"Successfully generated {n} test cases")
            )
            
        except Exception as e:
            self.root.after(0, lambda err=str(e): 
                messagebox.showerror("Error", f"An error occurred: {err}")
            )
        
        finally:
            # Reset UI
            self.root.after(0, lambda: self.progress.configure(value=0))
            self.root.after(0, lambda: self.status_var.set("Ready"))
            self.root.after(0, lambda: self.toggle_ui_state(True))
    
    def get_test_cases(self, category, user_story):
        """Call OpenAI API to generate test cases"""
        prompt = f"""
        You are a QA engineer. Generate detailed {category} for the following user story:
        
        User Story:
        {user_story}
        
        Provide test cases in a table format with the following columns:
        - Test Case ID
        - Test case
        - Expected Result"
        
        Note that the test case should be in following format:
        Use the phrasing pattern: 'Verify that (expected result) when (action taken).
        """
        
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a senior QA engineer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    
    def parse_response(self, response_text, category):
        """Parse the API response into structured test cases"""
        test_cases = []
        
        try:
            # Split the response into lines
            lines = response_text.strip().split('\n')
            
            # Process each line
            for line in lines:
                # Skip empty lines and header
                if not line.strip() or 'Test Case ID' in line or '---' in line:
                    continue
                
                # Split by '|' character
                parts = line.strip().split('|')
                if len(parts) >= 3:
                    # Clean up the parts
                    case_id = parts[0].strip()
                    test_case = parts[1].strip()
                    expected_result = parts[2].strip()
                    
                    # Add to test cases
                    test_cases.append({
                        "Test Case ID": case_id,
                        "Category": category,
                        "Test case": test_case,
                        "Expected Result": expected_result
                    })
                    
        except Exception as e:
            print(f"Error processing response: {str(e)}")
            
        return test_cases
    
    def save_to_csv(self, test_cases):
        """Save test cases to CSV file with automatic filename versioning"""
        if not test_cases:
            return

        base_file = self.output_file.get()
        base_dir = os.path.dirname(base_file) or "."  # Use current directory if empty
        base_name = os.path.basename(base_file)
        name, ext = os.path.splitext(base_name)

        output_file = os.path.join(base_dir, base_name)
        counter = 1

        # If file exists, generate a new name with a counter
        while os.path.exists(output_file):
            new_name = f"{name}_{counter}{ext}"
            output_file = os.path.join(base_dir, new_name)
            counter += 1

        try:
            with open(output_file, mode='w', newline='', encoding='utf-8') as file:
                fieldnames = ["Test Case ID", "Category", "Test case", "Expected Result"]
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(test_cases)

            # Open the directory containing the file
            directory = os.path.dirname(os.path.abspath(output_file))
            os.startfile(directory) if os.name == 'nt' else os.system(f'open "{directory}"')

        except Exception as e:
            messagebox.showerror("Error", f"Error writing to CSV: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TestCaseGeneratorApp(root)
    root.mainloop()