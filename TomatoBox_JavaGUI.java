import javax.swing.*;
import javax.swing.text.*;
import java.awt.*;
import java.awt.event.*;
import java.io.*;
import java.util.regex.*;

public class TomatoBox_JavaGUI {
    private JFrame frame;
    private JTextPane codeEditor;
    private StyledDocument doc;
    private JTextArea outputConsole;
    private JButton newSceneButton;
    private JButton playGameButton;
    private String currentFile = "GameCore.tmc";
    
    private SimpleAttributeSet keywordStyle;
    private SimpleAttributeSet stringStyle;
    private SimpleAttributeSet commentStyle;
    private SimpleAttributeSet directiveStyle;
    private SimpleAttributeSet normalStyle;
    
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            new TomatoBox_JavaGUI().createAndShowGUI();
        });
    }
    
    private void createAndShowGUI() {
        frame = new JFrame("TomatoBox Professional - Game Engine");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setSize(1000, 800);
        
        initStyles();
        
        JMenuBar menuBar = new JMenuBar();
        JMenu fileMenu = new JMenu("File");
        JMenuItem newItem = new JMenuItem("New Scene");
        newItem.addActionListener(e -> createNewScene());
        fileMenu.add(newItem);
        menuBar.add(fileMenu);
        frame.setJMenuBar(menuBar);
        
        JPanel toolbar = new JPanel();
        toolbar.setLayout(new FlowLayout(FlowLayout.LEFT));
        
        newSceneButton = new JButton("New Scene");
        newSceneButton.addActionListener(e -> createNewScene());
        toolbar.add(newSceneButton);
        
        playGameButton = new JButton("Play Game");
        playGameButton.setBackground(Color.ORANGE);
        playGameButton.addActionListener(e -> buildAndRunGame());
        toolbar.add(playGameButton);
        
        frame.add(toolbar, BorderLayout.NORTH);
        
        JSplitPane splitPane = new JSplitPane(JSplitPane.VERTICAL_SPLIT);
        splitPane.setResizeWeight(0.8);
        
        codeEditor = new JTextPane();
        doc = codeEditor.getStyledDocument();
        codeEditor.setFont(new Font("Microsoft YaHei", Font.PLAIN, 14));
        codeEditor.setBackground(new Color(30, 30, 30));
        codeEditor.setForeground(new Color(212, 212, 212));
        codeEditor.setCaretColor(Color.WHITE);
        codeEditor.addKeyListener(new KeyAdapter() {
            @Override
            public void keyReleased(KeyEvent e) {
                highlightSyntax();
            }
        });
        JScrollPane codeScrollPane = new JScrollPane(codeEditor);
        splitPane.setTopComponent(codeScrollPane);
        
        outputConsole = new JTextArea();
        outputConsole.setFont(new Font("Microsoft YaHei", Font.PLAIN, 12));
        outputConsole.setBackground(Color.BLACK);
        outputConsole.setForeground(new Color(0, 255, 0));
        outputConsole.setEditable(false);
        JScrollPane outputScrollPane = new JScrollPane(outputConsole);
        splitPane.setBottomComponent(outputScrollPane);
        
        frame.add(splitPane, BorderLayout.CENTER);
        
        loadDefaultScene();
        
        frame.setVisible(true);
    }
    
    private void initStyles() {
        keywordStyle = new SimpleAttributeSet();
        StyleConstants.setForeground(keywordStyle, new Color(86, 156, 214));
        
        stringStyle = new SimpleAttributeSet();
        StyleConstants.setForeground(stringStyle, new Color(206, 145, 120));
        
        commentStyle = new SimpleAttributeSet();
        StyleConstants.setForeground(commentStyle, new Color(106, 153, 85));
        
        directiveStyle = new SimpleAttributeSet();
        StyleConstants.setForeground(directiveStyle, new Color(197, 134, 192));
        
        normalStyle = new SimpleAttributeSet();
        StyleConstants.setForeground(normalStyle, new Color(212, 212, 212));
    }
    
    private void createNewScene() {
        String[] template = {
            "#*tomato-1.0.0.max // 全能版",
            "#加载拓展 : <*游戏引擎内核>;",
            "#<*stdlc> : <*简体中文>",
            "{",
            "    申请空间(1024); // 申请1MB内存",
            "}",
            "**main : {",
            "    输出 \"TomatoBox Engine v1.0 Start...\";",
            "    输出 \"Loading Assets...\";",
            "    输出 \"Game Loop Started.\";",
            "    结束并返回 0;",
            "}"
        };
        
        try {
            doc.remove(0, doc.getLength());
            doc.insertString(0, String.join("\n", template), normalStyle);
            highlightSyntax();
            log("New scene created successfully.");
        } catch (BadLocationException e) {
            log("Error creating new scene: " + e.getMessage());
        }
    }
    
    private void loadDefaultScene() {
        try {
            File file = new File(currentFile);
            if (file.exists()) {
                StringBuilder content = new StringBuilder();
                try (BufferedReader reader = new BufferedReader(
                        new InputStreamReader(new FileInputStream(file), java.nio.charset.StandardCharsets.UTF_8))) {
                    String line;
                    while ((line = reader.readLine()) != null) {
                        content.append(line).append("\n");
                    }
                }
                doc.remove(0, doc.getLength());
                doc.insertString(0, content.toString(), normalStyle);
                highlightSyntax();
                log("Loaded existing scene: " + currentFile);
            } else {
                createNewScene();
            }
        } catch (IOException | BadLocationException e) {
            log("Error loading scene: " + e.getMessage());
        }
    }
    
    private void buildAndRunGame() {
        try {
            try (BufferedWriter writer = new BufferedWriter(
                    new OutputStreamWriter(new FileOutputStream(currentFile), java.nio.charset.StandardCharsets.UTF_8))) {
                writer.write(codeEditor.getText());
            }
            log("Building Game Engine Core...");
            
            ProcessBuilder pb1 = new ProcessBuilder("python", "tmc_compiler.py", currentFile);
            pb1.directory(new File("."));
            Process p1 = pb1.start();
            int exitCode1 = p1.waitFor();
            
            if (exitCode1 == 0) {
                log("TMC compilation successful.");
                
                String cppFile = currentFile.replace(".tmc", ".cpp");
                String exeFile = currentFile.replace(".tmc", ".exe");
                
                log("Compiling Kernel to Binary...");
                ProcessBuilder pb2 = new ProcessBuilder("g++", cppFile, "-o", exeFile);
                pb2.directory(new File("."));
                Process p2 = pb2.start();
                
                try (BufferedReader reader = new BufferedReader(new InputStreamReader(p2.getErrorStream()))) {
                    String line;
                    while ((line = reader.readLine()) != null) {
                        log("Compiler Error: " + line);
                    }
                }
                
                int exitCode2 = p2.waitFor();
                
                if (exitCode2 == 0) {
                    log("Launching Game Scene...");
                    
                    ProcessBuilder pb3 = new ProcessBuilder(exeFile);
                    pb3.directory(new File("."));
                    Process p3 = pb3.start();
                    
                    try (BufferedReader reader = new BufferedReader(new InputStreamReader(p3.getInputStream()))) {
                        String line;
                        while ((line = reader.readLine()) != null) {
                            log(line);
                        }
                    }
                    
                    try (BufferedReader reader = new BufferedReader(new InputStreamReader(p3.getErrorStream()))) {
                        String line;
                        while ((line = reader.readLine()) != null) {
                            log("Game Error: " + line);
                        }
                    }
                    
                    p3.waitFor();
                    log("Game execution completed.");
                } else {
                    log("Compilation failed with exit code: " + exitCode2);
                }
            } else {
                log("TMC compilation failed with exit code: " + exitCode1);
            }
        } catch (Exception e) {
            log("Error building and running game: " + e.getMessage());
        }
    }
    
    private void highlightSyntax() {
        try {
            String code = codeEditor.getText();
            doc.setCharacterAttributes(0, code.length(), normalStyle, true);
            
            Pattern directivePattern = Pattern.compile("(^#.*?)(?=//|$)|(^\\*\\*.*?)(?=//|$)", Pattern.MULTILINE);
            Matcher directiveMatcher = directivePattern.matcher(code);
            while (directiveMatcher.find()) {
                String matched = directiveMatcher.group(1) != null ? directiveMatcher.group(1) : directiveMatcher.group(2);
                int start = directiveMatcher.start();
                int end = start + matched.length();
                doc.setCharacterAttributes(start, end - start, directiveStyle, true);
            }
            
            Pattern stringPattern = Pattern.compile("\".*?\"");
            Matcher stringMatcher = stringPattern.matcher(code);
            while (stringMatcher.find()) {
                doc.setCharacterAttributes(stringMatcher.start(), stringMatcher.end() - stringMatcher.start(), stringStyle, true);
            }
            
            String[] keywords = {"cout", "return", "break", "输出", "结束并返回", "跳出", "循环直到", "不成立", "申请空间"};
            for (String keyword : keywords) {
                highlightPattern(keyword, keywordStyle);
            }
            
            Pattern commentPattern = Pattern.compile("//.*");
            Matcher commentMatcher = commentPattern.matcher(code);
            while (commentMatcher.find()) {
                doc.setCharacterAttributes(commentMatcher.start(), commentMatcher.end() - commentMatcher.start(), commentStyle, true);
            }
        } catch (Exception e) {
            log("Highlight error: " + e.getMessage());
        }
    }
    
    private void highlightPattern(String pattern, SimpleAttributeSet style) {
        String code = codeEditor.getText();
        int index = 0;
        while ((index = code.indexOf(pattern, index)) != -1) {
            doc.setCharacterAttributes(index, pattern.length(), style, true);
            index += pattern.length();
        }
    }
    
    private void log(String message) {
        outputConsole.append(message + "\n");
        outputConsole.setCaretPosition(outputConsole.getDocument().getLength());
    }
}