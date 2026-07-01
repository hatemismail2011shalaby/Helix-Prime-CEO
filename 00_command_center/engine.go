package main

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
)

func main() {
	if len(os.Args) < 3 {
		fmt.Println("Helix Engine online. Type '<agent> <prompt>' or 'exit'.")
		reader := bufio.NewReader(os.Stdin)
		for {
			line, _ := reader.ReadString('\n')
			line = strings.TrimSpace(line)
			if line == "" {
				continue
			}
			lower := strings.ToLower(line)
			if lower == "exit" || lower == "quit" {
				fmt.Println("Helix Engine shutting down.")
				os.Exit(0)
			}
			parts := strings.Fields(line)
			if len(parts) < 2 {
				continue
			}
			agent := parts[0]
			prompt := strings.Join(parts[1:], " ")
			execPath, err := os.Executable()
			if err != nil {
				fmt.Printf("Error resolving executable path: %v\n", err)
				return
			}
			dir := filepath.Dir(execPath)
			routeToOrchestrator(dir, agent, prompt)
		}
		return
	}

	execPath, err := os.Executable()
	if err != nil {
		fmt.Printf("Error resolving executable path: %v\n", err)
		return
	}
	dir := filepath.Dir(execPath)
	agent := os.Args[1]
	prompt := os.Args[2]
	routeToOrchestrator(dir, agent, prompt)
}

func routeToOrchestrator(dir string, agent string, prompt string) {
	orchPath := filepath.Join(dir, "orchestrator.py")
	absoluteOrchPath, err := filepath.Abs(orchPath)
	if err != nil {
		fmt.Printf("Error getting absolute path: %v\n", err)
		return
	}

	cmd := exec.Command("python", absoluteOrchPath)
	payloadMap := map[string]string{
		"agent_name": agent,
		"prompt":     prompt,
	}
	payloadBytes, _ := json.Marshal(payloadMap)
	cmd.Stdin = bytes.NewReader(payloadBytes)

	out, err := cmd.Output()
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		return
	}
	fmt.Printf("Output: %s\n", out)
}
