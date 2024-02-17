package main

import (
	"bufio"
	"context"
	"fmt"
	"io"
	"log"
	"net"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strconv"
	"strings"
	"sync"
	"sync/atomic"
	"syscall"
)

func GetFreePort() (port string, err error) {
	var a *net.TCPAddr
	if a, err = net.ResolveTCPAddr("tcp", "localhost:0"); err == nil {
		var l *net.TCPListener
		if l, err = net.ListenTCP("tcp", a); err == nil {
			defer l.Close()
			port := l.Addr().(*net.TCPAddr).Port
			return strconv.Itoa(port), nil
		}
	}
	return
}

// App struct
type App struct {
	ctx      context.Context
	nodeProc *exec.Cmd
	pyProc   *exec.Cmd
	os       string
}

// NewApp creates a new App application struct
func NewApp() *App {
	os := runtime.GOOS
	app := App{os: os}
	fmt.Println("OS: ", os)
	return &app
}

// startup is called when the app starts. The context is saved
// so we can call the runtime methods
func (a *App) startup(ctx context.Context) {
	a.ctx = ctx
}

// Greet returns a greeting for the given name
func (a *App) Greet(name string) string {
	return fmt.Sprintf("Hello %s, It's show time!", name)
}

func (a *App) StartWorker() bool {
	if (a.nodeProc != nil) && (a.pyProc != nil) {
		return true
	}

	port, err := GetFreePort()
	if err != nil {
		panic(err)
	}
	log.Println("Found free port: ", port)

	exLoc, err := os.Executable()
	if err != nil {
		panic(err)
	}
	exPath := filepath.Dir(exLoc)
	log.Printf("Found path at : %s\n", exPath)

	if a.nodeProc == nil {
		nodePath := filepath.Join(exPath, "..", a.os, "nodeProc.exe")
		log.Printf("Starting node process with: %s %s\n", nodePath, port)
		cmd := exec.Command(nodePath, port)
		cmd.SysProcAttr = &syscall.SysProcAttr{HideWindow: true}

		stdout, err := cmd.StdoutPipe()
		if err != nil {
			log.Fatal(err)
		}
		stderr, err := cmd.StderrPipe()
		if err != nil {
			log.Fatal(err)
		}

		err = cmd.Start()

		if err != nil {
			log.Fatal(err)
		}

		go LogProcess("Node Process", &stdout, &stderr)

		a.nodeProc = cmd
	}

	if a.pyProc == nil {
		pyPath := filepath.Join(exPath, "..", a.os, "pyproc", "pyproc.exe")
		log.Printf("Starting node process with: %s\n", pyPath)
		cmd := exec.Command(pyPath, "--port", port)
		cmd.SysProcAttr = &syscall.SysProcAttr{HideWindow: true}

		stdout, err := cmd.StdoutPipe()
		if err != nil {
			log.Fatal(err)
		}
		stderr, err := cmd.StderrPipe()
		if err != nil {
			log.Fatal(err)
		}

		err = cmd.Start()

		if err != nil {
			log.Fatal(err)
		}

		go LogProcess("Python Process", &stdout, &stderr)

		a.pyProc = cmd
	}

	return true
}

func (a *App) KillWorker() bool {
	if (a.nodeProc == nil) && (a.pyProc == nil) {
		return true
	}

	if a.nodeProc != nil {
		a.nodeProc.Process.Kill()
		a.nodeProc = nil
		log.Printf("Killing Node Worker")
	}

	if a.pyProc != nil {
		a.pyProc.Process.Kill()
		a.pyProc = nil
		log.Printf("Killing Python Worker")
	}

	return true
}

func LogProcess(processName string, stdout *io.ReadCloser, stderr *io.ReadCloser) {

	var wg sync.WaitGroup
	var ops atomic.Uint32

	outch := make(chan string, 10)

	scannerStdout := bufio.NewScanner(*stdout)
	wg.Add(1)
	go func() {
		for scannerStdout.Scan() {
			text := scannerStdout.Text()
			if strings.TrimSpace(text) != "" {
				outch <- text
			}
		}
		ops.Add(1)
		wg.Done()
	}()

	scannerStderr := bufio.NewScanner(*stderr)
	wg.Add(1)
	go func() {
		for scannerStderr.Scan() {
			text := scannerStderr.Text()
			if strings.TrimSpace(text) != "" {
				outch <- text
			}
		}
		ops.Add(1)
		wg.Done()
	}()

	for {
		select {
		case text := <-outch:
			log.Printf("[%s] | %s", processName, text)
		}
		if ops.Load() >= 1 {
			wg.Wait()
			break
		}
	}
}
