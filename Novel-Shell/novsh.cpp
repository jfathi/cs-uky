/* Course:      CS-270-001: Systems Programming, University of Kentucky, FA2019
 * Authors:     Javid Fathi, javid.fathi@uky.edu (0632)
 *              Robert Taylor, willtaylor11@uky.edu (5718)
 * Project:     Programming Assignment 4: Novel Shell
 * Filename:    prog4.cpp
 * Compilation: g++ -Wall prog4.cpp -o novsh
 *              A Makefile should be used to compile the file correctly.
 * Algorithm:   See README documentation for additional information.
 * Synopsis:    See README documentation for additional information.
 * Last Edited: November 22, 2019
 * References:  See README documentation for additional information.
 */
//------------------------------------------------------------------------------
// SHELL-REFERENCED HEADER FILES AND REQUIRED MACROS
//------------------------------------------------------------------------------
#include <map>
#include <string>
#include <vector>
#include <fcntl.h>
#include <iomanip>
#include <string.h>
#include <iostream>
#include <unistd.h>
#include <stdlib.h>
#include <sys/wait.h>
#include <sys/stat.h>
#include <sys/types.h>
using namespace std;

#define MAX_VARS 1000
#define MAX_CHARS 256
#define MAX_BG_JOBS 29

#define ARG_INPUT_ERR 0
#define UNRECOGNIZED_CMD 1
#define NO_DIR_GIVEN 2
#define DIR_JUNK 3
#define VAR_JUNK 4
#define NO_VAL_ASSIGN 5
#define ASSIGNTO_FAIL 6

#define VAR_DEF_ARGS 3
#define NEWPROMPT_ARGS 2
#define LISTPROCS_ARGS 1
#define DIR_ARGS 2
#define BYE_ARGS 1

#define BACKGROUND_STR "<bg>"
#define NEWPROMPT_STR "newprompt"
#define LISTPROCS_STR "listprocs"
#define ASSIGNTO_STR "assignto"
#define VARIABLE_CHAR '$'
#define COMMENT_STR "!"
#define EQUAL_STR "="
#define RUN_STR "run"
#define DIR_STR "dir"
#define BYE_STR "bye"
//------------------------------------------------------------------------------
// CLASS FOR SHELL_TYPE
// Used to efficiently implement a body of variables and print-functions global
// to the shell in a protected and organized fashion.
//------------------------------------------------------------------------------
class shell_type
{
	private:
		vector <string> Tokens;         // Processed string tokens inputted by user
		vector <pid_t> Processes;       // List of processes active in shell <bg>
		map <string, string> Variables; // Map of string IDs & values of shell vars
		string Prompt;                  // String to indicate request for usr input
		bool exitCondition;             // Communicates when usr requests shell exit

	public:
		shell_type(string def_prompt);

		void set_Tokens(vector <string> new_set);
		vector<string> get_Tokens();
		void reset_Tokens();
		void disp_Tokens();

		void add_Process(pid_t process_id);
		void remove_Process(pid_t process_id);
		void kill_Processes();
		void disp_Processes();

		void set_variable(string identifier, string value);
		void get_variable(string identifier, string *value);

		void set_Prompt(string new_prompt);
		void error_Prompt();
		void disp_Prompt();

		void set_exitCondition_true();
		bool get_exitCondition();
};
//------------------------------------------------------------------------------
// IMPLEMENTATION OF SHELL_TYPE CLASS
//------------------------------------------------------------------------------
// shell_type: constructor for shell_type class
// Given:      Requested (default) string prompt;
// Initalizes: Shell containing:
//                  Default string prompt;
//                  Built-in variables (ShowTokens, PATH);
//                  Dynamic memory for storage of Tokens, Variables, Processes;
shell_type::shell_type(string def_prompt)
{
	Variables [ "ShowTokens" ] = "0";
	Variables [ "PATH" ] = "/bin:/usr/bin";
	int env_check = setenv("PATH", "/bin:/usr/bin", 1);
	if (env_check < 0)
	{
		perror("PATH");
		exit(EXIT_FAILURE);
	}
	Prompt = def_prompt;
	exitCondition = false;
}

// set_Tokens
// Replaces current set of string tokens with a new set;
// Given: new vector of token strings
void shell_type::set_Tokens(vector <string> new_set) { Tokens = new_set; }

// get_Tokens
// Returns: Vector of token strings edited and stored following user input
vector<string> shell_type::get_Tokens() { return Tokens; }

// reset_Tokens
// Removes all strings from current vector of string tokens
void shell_type::reset_Tokens()
{
	for (unsigned int i = 0; i < Tokens.size(); i++)
		Tokens.pop_back();
}

// disp_Tokens
// Format prints contents of token set to console (stdout)
// OUTPUTED FORMAT:
// Token = <token1_string>
// ...
// Token = <tokenN_string>
// --------------
void shell_type::disp_Tokens()
{
	for (unsigned int i = 0; i < Tokens.size(); i++)
		cout << "Token = " << Tokens[i] << endl;
	cout << "--------------\n";
}

// add_Process
// Stores the ID of a process running in the background of the shell;
// Exits if the number of background processes exceeds the maximum allowed (29).
void shell_type::add_Process(pid_t process_id)
{
	Processes.push_back(process_id);
	if (Processes.size() > MAX_BG_JOBS)
	{
		cerr << "Too many background jobs: " << Processes.size() << endl;
		exit(0);
	}
}

// remove_Process
// Given: ID of a process - assumedly running in the background of the shell;
// If the process ID given matches one held by the shell, then its reference is removed.
void shell_type::remove_Process(pid_t process_id)
{
	// Search for given process ID in local Processes vector
	unsigned int i = 0;
	while ((Processes[i] != process_id) && (i < Processes.size()))
		i++;
	if (i < Processes.size()) // If the process is found in the vector...
	{
		// ...have the process removed from the vector.
		for (unsigned int j = i; j < Processes.size()-1; j++)
			Processes[j] = Processes[j+1];
		Processes.pop_back();
	}
	else // If the process is not found in the vector...
		cout << "No such job to remove\n"; // ...output an error message.
		                                   // (This should be impossible.)
}

// kill_Processes
// Traverses vector of background processes for any exited processes;
// If found, the process is then reaped and reported to the console.
// Special Case: If the user has indicated a clean exit, then the function will
// kill all unreaped background processes before returning.
void shell_type::kill_Processes()
{
	// Traverse the vector of background processes.
	for (unsigned int i = 0; i < Processes.size(); i++)
	{
		int child_state;
		pid_t child_pid = Processes[i];
		waitpid(child_pid, &child_state, WNOHANG); // Check process and immediately return.
		if (WIFEXITED(child_state)) // If the process has exited...
		{ // ...then the child has been reaped!
			cout << "Reaping job with pid " << child_pid << "\n"; // Report case to console.
			remove_Process(child_pid); // Pop the completed process from the shell vector.
		}
		else if (exitCondition) // If process hasn't exited, but user indicates clean exit...
		{
			kill(child_pid, SIGKILL); // ...then the process must be killed.
			cout << "Reaping job with pid " << child_pid << "\n"; // Report case to console.
			remove_Process(child_pid); // Pop the completed process from the shell vector.
		}
	}
}

// disp_Processes
// Format prints contents of background process vector to console (stdout).
// OUTPUTED FORMAT:
// Processes:
// 	<process_id_1>
// 	...
// 	<process_id_n>
void shell_type::disp_Processes()
{
	cout << "Processes:" << endl;
	for (unsigned int i = 0; i < Processes.size(); i++)
		cout << "\t" << Processes[i] << endl;
}

// set_variable
// Given two strings, set the value of a new (or existing) string variable in the shell's private map;
// Exits if the maximum number of variables (1000) is exceeded.
void shell_type::set_variable(string identifier, string value)
{
	if ((identifier == "") || (value == ""))
	{
		cerr << "Variable cannot be defined with an empty string.\n";
		return;
	}
	if (strcmp(identifier.c_str(), "PATH") == 0) // If the variable ID is "PATH"...
	{
		// Set the environment variable "PATH" with the given string value
		int env_check = setenv("PATH", value.c_str(), 1);
		if (env_check < 0) // If setenv() fails...
		{
			perror("PATH"); // Output an error indicating such.
			// Set the environment variable "PATH" back to its previous string value
			env_check = setenv("PATH", Variables["PATH"].c_str(), 1);
			if (env_check < 0) // If this setenv fails...
			{
				perror("PATH"); // Output an error indicating such.
				exit(EXIT_FAILURE); // A serious error has occurred. Exit the shell.
			}
		}
	}
	Variables[identifier] = value; // Place the variable <id, val> into the shell's private map
	if (Variables.size() > MAX_VARS) // If the number of variables exceeds the
	                                 // maximum permitted (1001)...
	{
		cerr << "Too many variables: " << Variables.size() << "\n"; // ...output an error indicating such.
		exit(0); // Exit the shell.
	}
}

// get_variable
// Given a variable ID string, attempts to find a corresponding variable in the shell's map;
// If found, sets the contents of a given memory location equal to that of the variable's
// private value. Otherwise, it sets the contents of that memory location equal to an
// empty string.
void shell_type::get_variable(string identifier, string *value)
{
	// Traverse the shell's variable map in search of the requested variable.
	map<string, string>::iterator i;
	for (i = Variables.begin(); i != Variables.end(); i++)
	{
		if (identifier == i->first) // If the indexed variable ID equals the ID requested...
		{
			*value = i->second; // ...then set the variable value equal to the indexed variable value.
			return;
		}
	} // If the for-loop is exited, then the variable ID was not found.
	if (identifier == "ShowTokens") // If the varible ID is "ShowTokens"...
		cerr << "No ShowTokens variable\n"; // ...ouput an error indicating the ShowTokens variable
		                                    // does not exist. This error should be impossible.
	else
		cerr << "Variable " << identifier << " is not defined.\n"; // Output an error indicating that
		                                                           // the requested variable is undefined.
	*value = ""; // Set the variable value equal to an empty string.
}

// set_Prompt
// Sets the string prompt for user input equal to a user-inputted replacement.
void shell_type::set_Prompt(string new_prompt) { Prompt = new_prompt; }

// error_Prompt
// Displays an error message no input is processed for a user-requested newprompt.
void shell_type::error_Prompt() { cerr << "No prompt given." << endl; }

// disp_Prompt
// Displays the string prompt for user input to the console.
void shell_type::disp_Prompt() { cout << Prompt; }

// set_exitCondition_true
// Sets the (user-requested) state of the exitCondition to a true;
// Indicates a clean exit request.
void shell_type::set_exitCondition_true() { exitCondition = true; }

// get_exitCondition
// Returns the (user-requested) state of the shell;
// Used in loop conditionals and background process management;
// Shell may exit regardless of state.
bool shell_type::get_exitCondition() { return exitCondition; }
//------------------------------------------------------------------------------
// NOVEL SHELL - PARSER AND COMMAND EXECUTION FUNCTIONS
// Used to process and execute the user input to the shell.
//------------------------------------------------------------------------------
// std_cmd_error
// Prints a requested error message using information provided to the function;
// Excludes error messages specific to the shell class.
void std_cmd_error(int error_type, string prog_name, int args_needed)
{
	if (error_type == ARG_INPUT_ERR)
		cerr << prog_name << ": needs " << args_needed << " argument(s)\n";
	else if (error_type == UNRECOGNIZED_CMD)
    		cerr << "Unrecognized command.\n";
  else if (error_type == NO_DIR_GIVEN)
    		cerr << "No directory given\n";
	else if (error_type == DIR_JUNK)
		cerr << "Junk at end of cd command\n";
	else if (error_type == VAR_JUNK)
		cerr << "Junk at end of variable assignment\n";
	else if (error_type == NO_VAL_ASSIGN)
		cerr << "No value in assignment\n";
	else if (error_type == ASSIGNTO_FAIL)
		cerr << "incomplete assignto command\n";
}

// show_cmd_line
// Displays the processed tokens of the user's input to the shell (when "ShowTokens" = "1").
void show_cmd_line(shell_type *Shell)
{
	string show_bool;
	Shell->get_variable("ShowTokens", &show_bool);
	if (show_bool == "1")
		Shell->disp_Tokens();
}

// vector_pop_front
// Given a pointer vector, pop the first index out of frame.
void vector_pop_front(vector<string> *v)
{
	for (unsigned int i = 0; i < ((*v).size()-1); i++)
		(*v)[i] = (*v)[i+1];
	(*v).pop_back();
}

// run
// Given a command from the user, attempt execution of the command, either in
// the foreground or background of the program.
void run(shell_type *Shell)
{
	vector<string> Tokens = Shell->get_Tokens(); // Store tokens locally.

	pid_t process_id; // Initialize a process ID to be used by forking processes.
	process_id = fork(); // Fork the shell into two separate processes - parent and child.
	                     // This sets their process IDs to 0 for the child and some
											 // positive integer for the parent (which is the global value of
											 // child's process ID).

	if (process_id != 0) // If the process is the parent...
	{
		if (Tokens[Tokens.size() - 1] != BACKGROUND_STR) // ...and the command is not requested
		                                                 // to run in the background...
			process_id = waitpid(process_id, NULL, 0); // ...run command in the foreground;
			                                           // ...wait until the child process has been completed.
		else // But if the command is requested to run in the background...
			Shell->add_Process(process_id); // ...add the process ID (of the child) to shell vector.
		return; // ...and return to the shell.
	}
	else // If the process is the child...
	{
		if (Tokens[Tokens.size() - 1] == BACKGROUND_STR) // If the final token is "<bg>"...
			Tokens.pop_back(); // pop that token out of reference of the vector.
		if (Tokens.size() <= 1) // If only 1 (or somehow 0) token exist(s)...
			exit(EXIT_FAILURE); // ...the child process exits. No command is executed.

		vector_pop_front(&Tokens); // Pop the first token out of reference ("run").
		string temp_file = Tokens[0]; // Set a variable equal to the executable filename.

		// Fill a character pointer vector with the contents of the token string vector.
		vector<char*> args(Tokens.size()+1);
		for (unsigned int i = 0; i < Tokens.size(); i++)
			args[i] = &Tokens[i][0];

		int run_check = execvp(temp_file.c_str(), args.data()); // Execute requested command.
		if (run_check < 0) // If execution fails...
		{
			perror(temp_file.c_str()); // ...report an error to the console...
			exit(EXIT_FAILURE); // ...and exit with an indication of failure.
		}
		exit(EXIT_SUCCESS); // Exit the child process successfully.
	}
}

// assignto
// When successful, assigns the standard output of a requested command to a shell variable.
void assignto(shell_type *Shell)
{
	vector<string> Tokens = Shell->get_Tokens(); // Store tokens locally.
	vector_pop_front(&Tokens); // Pop the first token out of frame.
	if (Tokens.size() <= 1) // If less than two tokens remain...
	{
		std_cmd_error(ASSIGNTO_FAIL, "", 0); // ...then there was an error in the call.
		return;
	}
	
	string temp_file = "/tmp/novsh.out"; // Define a temporary output file location.

	pid_t process_id;    // Initialize a process ID to be used by forking processes.
	process_id = fork(); // Fork the shell into two separate processes - parent and child.
	                     // This sets their process IDs to 0 for the child and some
			     // positive integer for the parent (which is the global value of
			     // child's process ID).
	if (process_id != 0) // If the process is the parent...
	{
		process_id = waitpid(0, NULL, 0); // ...wait until the child process has been completed.

		FILE * tmp_file_ptr = fopen(temp_file.c_str(), "r"); // Open and read from the temporary file.

		int tmp_file = fileno(tmp_file_ptr); // Check the file descriptor value of the file pointer.
		if (tmp_file < 0) // If the file descriptor is negative...
			return; // ...there has been an error in accessing the file location. No variable is assigned.

		string var_ID = Tokens[0], var_Val = ""; // Initialize the prospective variable ID and value.

		char tmp_buf[MAX_CHARS]; // Create a buffer to temporarily store data from the file.

		while(!feof(tmp_file_ptr)) // While there is still data to be read from the file...
			if (fgets(tmp_buf, MAX_CHARS, tmp_file_ptr) != NULL) // ...import data to the temporary buffer...
				var_Val.append(tmp_buf); // ...and append the data as string values for the variable value string.

		fclose(tmp_file_ptr); // Close the temporary file.

		if (var_Val.length() == 0) // If no data was transmitted...
			return; // then no variable is assisgned.
		else
			Shell->set_variable(var_ID, var_Val); // Otherwise, set a variable with the ID & value given.
	} // End of Parent Process
	else // If the process is the child...
	{
		FILE * tmp_file_ptr = fopen(temp_file.c_str(), "w"); // Open and overwrite the temporary file.

		int tmp_file = fileno(tmp_file_ptr); // Check the file descriptor of the file pointer.
		if (tmp_file < 0) // If the file descriptor is negative...
		{
			perror(temp_file.c_str()); // ...there has been been an error in accessing the file location.
			exit(EXIT_FAILURE); // Child process is exited. No variable is assigned.
		}
		dup2(tmp_file, 1); // Pipe standard output (stdout) to temporary file stream.

		int close_check = fclose(tmp_file_ptr); // Close the temporarry file.
		if (close_check < 0) // If closing the file failed,
		{
			perror(temp_file.c_str()); // ...a serious error has occurred.
			exit(EXIT_FAILURE); // The child process is exited. No variable is assigned.
		}

		vector_pop_front(&Tokens); // Pop the first index of the token vector;
		                           // All that remains is the filename and parameters.
		string run_file = Tokens[0]; // Set a variable equal to the filename.

		// Fill a character pointer vector with the contents of the token string vector.
		vector<char*> args(Tokens.size()+1);
		for (unsigned int i = 0; i < Tokens.size(); i++)
			args[i] = &Tokens[i][0];

		int run_check = execvp(run_file.c_str(), args.data()); // Execute requested command.
		if (run_check < 0) // If execution fails...
		{
			perror(run_file.c_str()); // ...report an error to the console.
			exit(EXIT_FAILURE); // The child process is exited. No variable is assigned.
		}
		exit(EXIT_SUCCESS); // The child process is exited. Given that the command
		                    // printed something to stdout, a variable will be assigned.
	}
}

// newprompt
// When prompted, attempt to change the shell's prompt to a string given by the user.
void newprompt(shell_type *Shell)
{
	vector<string> Tokens = Shell->get_Tokens(); // Store tokens locally.
	if (Tokens.size() < NEWPROMPT_ARGS) // If only one token exists...
    		Shell->error_Prompt(); // ...output an error indicating no new prompt was given.
  	else if (Tokens.size() > NEWPROMPT_ARGS) // If more than the required 2 tokens exist...
    		std_cmd_error(ARG_INPUT_ERR, NEWPROMPT_STR, NEWPROMPT_ARGS-1); // ...output error.
	else // If exactly two tokens exist...
	    	Shell->set_Prompt(Tokens[1]); // ...set the shell prompt equal to the second token.
}

// dir
// When prompted, attempt to change the working directory of the shell to a location indicated by user.
void dir(shell_type *Shell)
{
	vector<string> Tokens = Shell->get_Tokens(); // Store tokens locally.
	if (Tokens.size() < DIR_ARGS) // If only one token exists...
		std_cmd_error(NO_DIR_GIVEN, "", 0); // ...ouput an error indicating no directoy given.
	else if (Tokens.size() > DIR_ARGS) // If more than two tokens exist...
		std_cmd_error(DIR_JUNK, "", 0);  // ...output an error indicating junk at end of call.
	else // If exactly two tokens exist...
	{
		string requested_dir = Tokens[1]; // ...then the second token is the desired directory.
		int file_check = chdir(requested_dir.c_str()); // Attempt to change WD to desired dir.
		if (file_check < 0) // If attempt to change directories is unsuccessful...
			perror(requested_dir.c_str()); // ...then the requested directory does not exist.
	}
}

// listprocs
// When prompted, attempt to display a list of the processes running in the background of the shell.
void listprocs(shell_type *Shell)
{
	vector<string> Tokens = Shell->get_Tokens(); // Store shell tokens locally.
	if (Tokens.size() != LISTPROCS_ARGS) // If more than one token exists...
		std_cmd_error(ARG_INPUT_ERR, LISTPROCS_STR, LISTPROCS_ARGS-1); // ...output a call error
  else
		Shell->disp_Processes(); // Otherwise, print the shell's background processes.
}

// bye
// When prompted, prepare the shell for a user-requested (clean) exit of the program.
void bye(shell_type *Shell)
{
	vector<string> Tokens = Shell->get_Tokens(); // Store tokens locally.
	if (Tokens.size() != BYE_ARGS) // If more than one token exists...
		std_cmd_error(ARG_INPUT_ERR, BYE_STR, BYE_ARGS-1); // ...output a call error.
	else
		Shell->set_exitCondition_true(); // Otherwise, prepare system for a clean exit.
}

// variable_definition
// When successful, creates or redefines a shell variable with the value and ID inputted
// by the user. Given its placement on the if-else tree of run_cmd_line, if the processed
// tokens do not represent a variable definition call, the program recognizes
// and reports the user input as an unrecognized command.
void variable_definition(shell_type *Shell)
{
	vector<string> Tokens = Shell->get_Tokens(); // Store shell tokens locally.
	if (Tokens.size() >= VAR_DEF_ARGS) // If at least 3 shell tokens have been processed...
	{
		if (Tokens[1] == EQUAL_STR) // ...and the second token is "="...
		{
			if (Tokens.size() == VAR_DEF_ARGS) // ...and exactly 3 shell tokens exist...
			{
				if (Tokens[2] != "") // ...and the third token has some value...
					Shell->set_variable(Tokens[0], Tokens[2]); // ...then try to set a shell variable.
				else // If the third token has no value...
					std_cmd_error(NO_VAL_ASSIGN, "", 0); // ...then output an error indicating such.
			}
			else // If more than 3 shell tokens exist...
				std_cmd_error(VAR_JUNK, "", 0); // ...then output an error indicating such.
		}
		else // If the second token is NOT "="...
			std_cmd_error(UNRECOGNIZED_CMD, "", 0); // ...then this is an unrecognized command.
	}
	else // If less than 3 shell tokens have been processed...
		std_cmd_error(UNRECOGNIZED_CMD, "", 0); // ...then this is an unrecognized command.
}

// run_cmd_line
// Uses the processed, tokenized user input to direct the shell to the correct
// execution process of the parser.
void run_cmd_line(shell_type *Shell)
{
	if ((Shell->get_Tokens()).size() > 0) // If any input has been processed...
	{
		string req_cmd = (Shell->get_Tokens())[0]; // ...grab the first token...
		// ...and attempt to execute the indicated command.
		if (req_cmd == COMMENT_STR) { return; } // "! anyText" (This is a comment; ignore and return.)
  		else if (req_cmd == BYE_STR) { bye(Shell); } // "bye"
		else if (req_cmd == DIR_STR) { dir(Shell); } // "dir requested_dir"
		else if (req_cmd == RUN_STR) { run(Shell); } // "run cmd param* [<bg>]"
 	 	else if (req_cmd == ASSIGNTO_STR) { assignto(Shell); } // "assignto variable cmd param*"
  		else if (req_cmd == LISTPROCS_STR) { listprocs(Shell); } // "listprocs"
		else if (req_cmd == NEWfPROMPT_STR) { newprompt(Shell); } // "newprompt prompt"
  		else { variable_definition(Shell); } // "variable_ID = variable_Value"
	}
}

// set_variable_Tokens
// Checks initiallly scanned tokens for requested variable defintions;
// Sets such ($)variable tokens equal to the stored (or empty/undefined) values.
vector<string> set_variable_Tokens(shell_type *Shell)
{
	vector<string> new_Tokens = Shell->get_Tokens(); // Store tokens locally.
	// The following is a nested for-loop to search every character of every index
	// of the initialized token vector.
	for (unsigned int i = 0; i < new_Tokens.size(); i++)
	{
		for (unsigned int j = 0; j < new_Tokens[i].length(); j++)
		{
			if (new_Tokens[i][j] == VARIABLE_CHAR) // If any character in a string equals "$"...
			{ // ...then the rest of that string is the identifier for a shell variable.
				string req_variable = (new_Tokens[i]).substr((j+1),
					((new_Tokens[i]).length()-1));
				string req_variable_val; // Initialize a string for the variable value...
				Shell->get_variable(req_variable, &req_variable_val); // ...and get the value from the shell.
				if (j > 0) // So long as "$" is not the first character...
				{
					string kept_string = (new_Tokens[i]).substr(0, j); // ...keep the initial characters of the string...
					new_Tokens[i] = kept_string + req_variable_val; // ..and alter the value of token to equal its initial
					                                                // characters plus the value of the requested variable.
				}
				else
					new_Tokens[i] = req_variable_val; // Otherwise, the token now equals the requested variable value.
			}
		}
	}
	return new_Tokens; // return the fully processed set of tokens.
}

// parse_cmd_line - driver for execution parser and token processing
// Processes and - if possible - executes the user input to the console.
void parse_cmd_line(shell_type *Shell)
{
	vector <string> new_Tokens = set_variable_Tokens(Shell); // Check user input for
	                                                         // references to shell variables
	Shell->set_Tokens(new_Tokens); // Set shell tokens equal to altered user input; now
	                               // represents effective command line.
	show_cmd_line(Shell); // If requested by user (via ShowTokens assignment),
	                      // show the input-tokens stored and processed by the shell.
	run_cmd_line(Shell);  // If possible - execute the contents of the command line.
}
//----------------------------------------------------------------------------------------
// SHELL PROGRAM - SCANNER FUNCTIONS
//----------------------------------------------------------------------------------------
// scanner - primary token scanner
// Given: a NULL-terminated string of variable length and composition
// Returns: Vector of inputted token string values
vector<string> scanner(string userInput)
{
	vector<string> retTokens; // A vector of strings to be returned
	string str = userInput;
	string token; // A string to represent a single token, it will be reset to nothing
	              // after being pushed into the vector
	int cutIndex1, cutIndex2; // cutIndex1 - An index of a desired character, " " or "\""
	                          // cutIndex2 - Similar to cutIndex1, used when cutIndex1 has already been used
	while(str.length() != 0)  // While the user's input string hasn't been completely scanned...
	{
		if (str[0] == ' ') // If the first character is a space...
			str = str.substr(1, str.length()); // ...move to the next character.
		else if (str.find_first_of("\"") < str.find_first_of(" ")) // If there is a quote before there is a space...
		{
			cutIndex1 = str.find_first_of("\""); // ...set cutIndex1 to the index of the quote.
			str = str.substr(cutIndex1 + 1, str.length()); // Cut the string from cutIndex to the end of the string
			cutIndex2 = str.find_first_of("\""); // Set cutIndex2 to the next quote in the string
			if (cutIndex2 == -1) // If there is no other quote in the string...
			{
				cerr << "Unterminated quoted string\n"; // Print an error message...
				return vector<string>(); // ...and return an empty vector.
			}
			token = str.substr(0, cutIndex2); // Set the token equal to the part of the
			                                  // string inside the found set of quotes.
			retTokens.push_back(token); // Put the token in the vector
			if (((int)str.find_first_of(" ")) == -1) // If the string doesn't have any spaces in it,
			{
				if (str.substr(cutIndex2, str.length()).length() == 1) // ...and if the length of the string
				                                                       // after the token has been cut equals 1,
					return retTokens; // return the tokens as a complete vector.
			}
			else // If the string does have spaces in it...
				str = str.substr(cutIndex2 + 1, str.length()); // ...cut the string and restart the loop.
		}
		else if (((int)str.find_first_of(" ")) == -1) // If there is no space character in the string
		                                              // and no quote character was found,
		{
			token = str.substr(0, str.length()); // ...then the whole string is a single token...
			retTokens.push_back(token); // ...which should be placed into the vector...
			return retTokens; // ...which is then returned.
		}
		else if (((int)str.find_first_of(" ")) != -1) // If there is a space character and no quote
		                                              // character comes before it...
		{ // ...then that index marks the first character of the next token.
			cutIndex1 = str.find_first_of(" ");
			token = str.substr(0, cutIndex1);
			retTokens.push_back(token);
			str = str.substr(cutIndex1 + 1, str.length()); // Cut the string to the first non-space character.
		}
	}
	return retTokens; // Return the vector after the while loop has finished.
}
// scan_cmd_line - input scanner and driver
// Given: Access to initialized Shell
// Edits: Contents of Shell - converts user input to vector of string tokens
// Exits: If requested by user via EOF signal <Control-D>
void scan_cmd_line(shell_type *Shell)
{
	string userInput; // Initialize a string variable for the user's input...
	vector<string> init_Tokens; // ...and the tokenized vector of that input.
	while (getline(cin, userInput)) // While the user is inputting data...
	{
		// Ensure that the input is within the bounds permitted.
		if (userInput.length() > MAX_CHARS)
		{ // If not, output an error message and set the token vector equal to an empty vector.
			cerr << "Maximum input permitted is " << MAX_CHARS << " characters. No input stored.\n";
			init_Tokens = vector<string>();
		}
		else // If the input is within the bounds permitted...
			init_Tokens = scanner(userInput); // Set the input vector equal to the set of initial tokens.
		Shell->set_Tokens(init_Tokens); // Then, set the shell's tokens equal to those of the local vector.
		return;
	}
	// The following only occurs if the loop is terminated with the input <Control+D>
	Shell->set_Tokens(vector<string>()); // Set the shell's tokens equal to those of an empty vector.
	Shell->set_exitCondition_true(); // Prepare the shell for a clean exit of the program.
}
//----------------------------------------------------------------------------------------
// SHELL - PRIMARY LOOP (primary_loop)
// Used as the bridge between the shell, the driver, the parser and the scanner for the
// duration of the program. Function will return to main upon requst of clean exit.
//----------------------------------------------------------------------------------------
void primary_loop(shell_type *Shell)
{
	while (!(Shell->get_exitCondition())) // While the user has not requested to exit...
	{
		Shell->disp_Prompt();  // ...display a prompt for input to console...

		scan_cmd_line(Shell);  // ...store and tokenize user input...

		parse_cmd_line(Shell); // ...parse and - if possible - execute user input...

		Shell->reset_Tokens(); // ...then pop the user input from the frame...

		Shell->kill_Processes(); // ...and try to reap/kill background processes.
	}
}
//----------------------------------------------------------------------------------------
// PROGRAM DRIVER FUNCTION (main)
// Used to initiate novel shell
//----------------------------------------------------------------------------------------
int main()
{
	shell_type myShell("novsh > "); // Initalizes and constucts shell in frame
	primary_loop(&myShell);         // Controls and executes shell per user cmds
	return 0;
}
