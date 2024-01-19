# -*- coding: utf-8 -*-
"""
Date: Oct 2023

@author: Alex Maier

Description: Finds the nearest E24, E48, or E96 value for a given resistor. 
             Also finds the color band for the resistor. 
             Resistor must be from 1 - 10MΩ.
"""

# =============================================================================
# ----- MODULE IMPORTS --------------------------------------------------------
# =============================================================================
import tkinter as tk
from tkinter import ttk, Menu

# =============================================================================
# ----- MAIN ROUTINE ----------------------------------------------------------
# =============================================================================
def main():
    root = tk.Tk()
    root.title("Resistor Calculator")

    # Create a frame for all widgets
    frame = ttk.Frame(root, padding="5")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    # Label and entry for R
    ttk.Label(frame, text="R =").grid(row=0, column=0, sticky=tk.E, padx=2, pady=5)
    resistor_value = tk.StringVar()
    ttk.Entry(frame, textvariable=resistor_value).grid(row=0, column=1, padx=2, pady=5)

    # Create a StringVar for the unit and set its default value
    unit = tk.StringVar(value='Ω')

    # Add the combo element for units
    units = ['Ω', 'kΩ', 'MΩ']
    unit_combobox = ttk.Combobox(frame, textvariable=unit, values=units, state="readonly", width=3)
    unit_combobox.grid(row=0, column=2, sticky=tk.W, padx=2, pady=5)

    # Radiobuttons for E24, E48, E96
    resistor_type = tk.StringVar()
    ttk.Radiobutton(frame, text="E24: ±5%", variable=resistor_type, value="E24").grid(row=1, column=0, sticky=tk.N, padx=5, pady=5)
    ttk.Radiobutton(frame, text="E48: ±2%", variable=resistor_type, value="E48").grid(row=1, column=1, sticky=tk.N, padx=5, pady=5)
    ttk.Radiobutton(frame, text="E96: ±1%", variable=resistor_type, value="E96").grid(row=1, column=2, sticky=tk.N, padx=5, pady=5)
    
    # Error message display
    error_message = tk.StringVar()
    ttk.Label(frame, textvariable=error_message, foreground="red").grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
    
    def on_search():
        # Check if input is valid
        try: 
            value = float(resistor_value.get())
        except ValueError:
            error_message.set("Invalid input")
        else:
            try:
                selected_unit = unit.get()
    
                # Convert value based on the selected unit
                if selected_unit == 'kΩ':
                    value *= 1000
                elif selected_unit == 'MΩ':
                    value *= 1000000
    
                # Find nearest value
                tolerance = resistor_type.get()
                r_data = find_nearest_resistor(value, tolerance)
                error_message.set('')  # clear any previous error message
                nearest = r_data['value']
                p_ten = r_data['p_ten']
                
                # Adjust if nearest is 1000 
                if nearest == 1000:
                    nearest = 100
                    p_ten += 1
                
                
                # Use power of ten to print magnitude correctly
                match p_ten:
                    case -2: nearest = (str(nearest/100) + 'Ω')
                    case -1: nearest = (str(nearest/10)  + 'Ω')
                    case  0: nearest = (str(nearest)     + 'Ω')
                    case  1: nearest = (str(nearest/100) + 'kΩ')
                    case  2: nearest = (str(nearest/10)  + 'kΩ')
                    case  3: nearest = (str(nearest)     + 'kΩ')
                    case  4: nearest = (str(nearest/100) + 'MΩ') 
                    case  5: nearest = (str(nearest/10)  + 'MΩ')
                
                nearest_value_var.set(nearest)
            
                # Find color band
                r_data = find_colors(r_data)
                seperator = '-'
                colors = seperator.join(r_data['colors'])
                color_code_var.set(colors)
        
            # Catch and print other errors next to search button
            except Exception as e:  
                error_message.set(str(e))
                
    # Search button
    ttk.Button(frame, text="Search", command=on_search).grid(row=2, column=0, padx=5, pady=15)        
    
    # Bind <Enter> to search
    root.bind("<Return>", lambda event=None: on_search())

    # Nearest value display
    ttk.Label(frame, text="Nearest Value:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
    nearest_value_var = tk.StringVar()
    ttk.Label(frame, textvariable=nearest_value_var).grid(row=3, column=1, padx=5, pady=5)

    # Color code 
    ttk.Label(frame, text="Color Code:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
    color_code_var = tk.StringVar()
    ttk.Label(frame, textvariable=color_code_var).grid(row=4, column=1, padx=5, pady=5)

    # ===== Menu and submenu functions ========================================
    # Exit the program 
    def exit_command():
        root.destroy()
    
    
    # Paste the clipboard into the resistor value input
    def paste_value_command():
        try:
            # Get the value from the clipboard
            clipboard_value = root.clipboard_get()
        
            # Set the value to the resistor_value entry field
            resistor_value.set(clipboard_value)
        except tk.TclError:
            # If there's nothing in the clipboard or non-text data
            pass
        
        
    # Copy the results to the clipboard    
    def copy_results_command():
        # Clear any existing content in the clipboard
        root.clipboard_clear()
    
        # Get the results
        nearest_value_result = nearest_value_var.get()
        color_code_result = color_code_var.get()
        
        # Construct the string to be copied
        results_string = (f"Nearest Value: {nearest_value_result}\nColor Code: {color_code_result}")

        # Append the string to the clipboard
        root.clipboard_append(results_string)
    
    
    # Display window with program info
    def about_command():
        # Create a new top-level window
        about_window = tk.Toplevel(root)
        about_window.title("About")
        
        description = (
            "Resistor Calculator v1.0\n"
            "\n"
            "Date: Oct 2023\n"
            "Author: Alex Maier\n"
            "\n"
            "Finds the nearest E24, E48, or E96 value for a given resistor.\n" 
            "Also finds the color band for the resistor. Resistor value\n" 
            "must be from 1 - 10MΩ."
        )
        
        lbl_description = tk.Label(about_window, text=description, padx=10, pady=10, justify=tk.LEFT)
        lbl_description.pack(pady=20)
        
        # Add a close button
        btn_close = ttk.Button(about_window, text="Close", command=about_window.destroy)
        btn_close.pack(pady=10)
        
    # Create main menu bar
    menu_bar = Menu(root)
    root.config(menu=menu_bar)    
        
    # Create File submenu
    file_menu = Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="Search", command=on_search)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=exit_command)
    
    # Create Edit submenu
    edit_menu = Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Edit", menu=edit_menu)
    edit_menu.add_command(label="Paste Value", command=paste_value_command)
    edit_menu.add_command(label="Copy Results", command=copy_results_command)

    # Create Help submenu
    help_menu = Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Help", menu=help_menu)
    help_menu.add_command(label="About", command=about_command)

    root.mainloop()
    return


# =============================================================================
# ----- FUNCTIONS & DEFINITIONS -----------------------------------------------
# =============================================================================

# E24 Values
E24 = (100,110,120,130,150,160,180,200,220,240,270,300,330,360,390,430,470,510,
560,620,680,750,820,910,1000)

# E48 Values
E48 = (100,105,110,115,121,127,133,140,147,154,162,169,178,187,196,205,215,226,
237,249,261,274,287,301,316,332,348,365,383,402,422,442,464,487,511,536,
562,590,619,649,681,715,750,787,825,866,909,953,1000)

# E96 Values
E96 = (100,102,105,107,110,113,115,118,121,124,127,130,133,137,140,143,147,150,
154,158,162,165,169,174,178,182,187,191,196,200,205,210,215,221,226,232,
237,243,249,255,261,267,274,280,287,294,301,309,316,324,332,340,348,357,
365,374,383,392,402,412,422,432,442,453,464,475,487,499,511,523,536,549,
562,576,590,604,619,634,649,665,681,698,715,732,750,768,787,806,825,845,
866,887,909,931,953,976,1000) 

# Color band for each digit on a resistor
Colors = {0:'black', 1:'brown', 2:'red', 3:'orange', 4:'yellow', 5:'green',
          6:'blue', 7:'violet', 8:'gray', 9:'white'}

# Color band for powers of ten
Power_Colors = {0:'black', 1:'brown', 2:'red', 3:'orange', 4:'yellow', 
                5:'green', 6:'blue', -1:'gold', -2:'silver'}

# Color band for tolerance
Tolerance_Colors = {'E24':'gold', 'E48':'red', 'E96':'brown'}


# ===== Find nearest R value ==================================================
def find_nearest_resistor(value, tolerance):
    ''' Finds nearest resistor value for given tolerance '''
    # Check if input is valid
    try:
        value = float(value)
    except ValueError:
        raise ValueError("Invalid input")
    else:    
        # Setup
        p_ten = 0
    
        # Check if resistor value is zero or below
        if value <= 0:
            raise ValueError("Enter 1 - 10MΩ")
    
        # Convert user value to between 100-1000 and keep track of power of ten
        while value < 100:
            value = value*10
            p_ten -= 1
        while value > 1000:
            value = value/10
            p_ten += 1   
                
        # Check if resistor value is in range  
        if (p_ten <= -3) or (p_ten >= 5):
            raise ValueError("Enter 1 - 10MΩ") 
        else:
            # Find nearest value based on selected tolerance 
            match tolerance:
                case "E24": nearest = min(E24, key=lambda x: abs(x-value))
                case "E48": nearest = min(E48, key=lambda x: abs(x-value))
                case "E96": nearest = min(E96, key=lambda x: abs(x-value))
                case     _: raise ValueError("Choose a tolerance")

            r_data = {'value':nearest, 'p_ten':p_ten, 'tolerance': tolerance, 'colors':[]}
            return r_data       


# ===== Find resistor colors ==================================================
def find_colors(r_data : dict) -> dict:
    ''' Finds color code for given resistor '''
    value = r_data['value']
    p_ten = r_data['p_ten']
    tolerance = r_data['tolerance']
    
    # Make sure band is 5 colors
    if value == 1000:
        value = 100
        p_ten += 1
        
    # Convert resistor value to digits and then map digits to 'Colors' dictionary 
    r_digits = [int(i) for i in str(value)]
    color_list = list(map(Colors.get, r_digits))
    
    # Remove third integer band if tolerance is E24
    if r_data['tolerance'] == "E24":
        color_list.pop(2)
    
    # Append the correct colors for magnitude based on tolerance
    if tolerance == "E24":
        color_list.append(Power_Colors[p_ten + 1])
    else:
        color_list.append(Power_Colors[p_ten])
        
    # Append tolerance color    
    color_list.append(Tolerance_Colors[tolerance])
    
    # Add colors to data dictionary and return
    r_data['colors'] = color_list 
    return r_data
    

# =============================================================================
# ----- INVOKE MAIN ROUTINE ---------------------------------------------------
# =============================================================================
if __name__ == '__main__':
    main()


# =============================================================================
# ----- END OF FILE -----------------------------------------------------------
# =============================================================================
