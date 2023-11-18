"""
오토마타와 컴파일러(SW)
과제명: 미니 C 컴파일러 과제
학과: 소프트웨어학과
학번/이름: 32202970 윤예진
제출일: 23.11.18
"""


# 토큰 테이블 클래스
class TokenTable:
    ### 생성자
    def __init__(self):
        ### 명령어(OP) 테이블
        # 10 ~ 24번
        # 30 ~ 39번
        self.opTable = dict()
        self.opTable['tident'] = 3
        self.opTable['tconst'] = 4
        self.opTable['tint'] = 5
        self.opTable['treal'] = 6

        self.opList = ['+', '-', '*', '/', '%', '=', '!', '&&', '||', '==', '!=', '<', '>', '<=', '>=']
        for i in range(0, 15):
            self.opTable[self.opList[i]] = i+10
        
        self.specialList = ['[', ']', '{', '}', '(', ')', ',', ';', '‘', '’']
        for i in range(0, 10):
            self.opTable[self.specialList[i]] = i + 30

        ### 예약어 테이블
        # 40 ~ 52번
        self.reservedTable = dict()
        self.reservedList = ['If', 'While', 'For', 'Const', 'Int', 'Float', 'Else',
                        'Return', 'Void', 'Break', 'Continue', 'Char', 'Then']

        for i in range(0, 13):
            self.reservedTable[self.reservedList[i]] = i+40

        ### 심볼 테이블
        # 60번 ~
        self.symbolTable = dict()

        ### 공백
        self.blank = [' ', '\x0A', '\x0D']           # 공백, 줄바꿈, 캐리지리턴


# 미니 컴파일러(스캐너) 클래스
class MiniCompiler:
    ### 생성자
    def __init__(self):
        self.TokTB = TokenTable()                   # 토큰 테이블
        self.index = 0
        self.token = ''                             # 현재까지 인식된 토큰
        self.isEOF = False

    # 미니 컴파일러 실행
    def Initial(self, source):
        self.index = 0
        self.isEOF = False
        
        while(True):
            self.token = ''

            # 처음 심볼 하나를 읽고 상태(State)를 분류
            # 각 상태마다 해당하는 처리 메소드를 호출, 메소드는 공백이 나올 때까지 읽음.
            # EOF에 도달하면 False 리턴, False 리턴 받았을 시 전체 스캐너 종료
            try:
                s = source[self.index]
            # EOF 도달 시
            except EOFError:
                self.isEOF = True
                break

            # 공백 문자(space, 개행 문자)라면 무시하고 다음 문자를 읽는다
            if(s in self.TokTB.blank):
                self.index += 1
                continue
            
            # 연산자 State
            if(s in self.TokTB.opList):
                self.token += s
                self.index += 1
                self.OperSpecial(source)               # 연산자 State에서 처리
            
            # 특수 기호 State
            elif(s in self.TokTB.specialList):
                self.token += s
                self.index += 1
                self.OperSpecial(source)                # 특수문자 State에서 처리

            # 예약어 State  (문자열과 만난 경우)
            elif('a' <= s <= 'z' or 'A' <= s <= 'Z'):
                self.token += s
                self.index += 1
                self.ReservedWord(source)           # 예약어 State에서 처리
                
            # 정수 State
            elif('1' <= s <= '9'):
                self.token += s
                self.index += 1
                self.DecimalInt(source)             # 10진 정수 State에서 처리

            # Zero State
            # 숫자 0 or 0으로 시작하는 경우 (8진수, 16진수)
            elif('0' == s):
                self.token += s
                self.index += 1
                self.Zero(source)                   # Zero State에서 처리
            
            # 숫자/알파벳 이외의 문자 처리
            else:
                # 공백이 나올 때까지 토큰을 읽는다
                while(s not in self.TokTB.blank):
                    try:
                        s = source[self.index]
                    # EOF 도달 시
                    except EOFError:
                        self.isEOF = True
                        break
                    
                    self.token += source[self.index]
                    self.index += 1

        # 스캐너 종료
        print("\n <--- End of File--->")


    # 연산자 및 특수문자 State
    def OperSpecial(self, source):                
        s = 'init'

        # 공백이 나올 때까지 토큰을 읽는다
        while(s not in self.TokTB.blank):
            # / 로 시작하는 토큰일 경우
            if(self.token == '/'):
                try:
                    s = source[self.index]
                # EOF 도달 시
                except EOFError:
                    self.isEOF = True
                    break
                
                # 주석 처리 State
                if(s == '?'):
                    self.token += s; self.index += 1
                    self.Comment(source)        # 주석 State에서 처리
                    return
            
            # 작은 따옴표로 시작하는 토큰일 경우
            if(self.token == '‘'):
               self.PrintToken('OP')
               self.token = ''; self.index += 1
               self.Const(source)           # 상수 State에서 처리
               return
            
            self.token += s; self.index += 1

        tokNum = self.TokTB.opTable.get(self.token)

        # 토큰 출력
        self.PrintToken('OP')
        if(not self.isEOF):
            self.index += 1
        return
    
    
    # 주석 처리 State       (/? 까지 읽은 상태)
    # 주석은 ?/가 나올 때까지 읽고 주석 처리 완료 메세지를 출력
    def Comment(self, source):
        try:
            s = source[self.index]
        # EOF 도달 시
        except EOFError:
            self.isEOF = True
            
        # 공백이 나올 때까지 토큰을 읽는다
        while(s not in self.TokTB.blank):
            # ? 로 시작하는 토큰일 경우
            if(self.token == '?'):
                try:
                    s = source[self.index]
                # EOF 도달 시
                except EOFError:
                    self.isEOF = True
                    break
                
                # 주석 닫음
                if(s == '/'):
                    self.token += s; self.index += 1
                    self.PrintComment()
                    return
                
            self.token += s; self.index += 1
            try:
                s = source[self.index]
            # EOF 도달 시
            except EOFError:
                self.isEOF = True
                break
            
        self.PrintComment()
        if(not self.isEOF):
            self.index += 1
        return
    
    # 상수 State    (여는 작은 따옴표까지 읽은 상태)
    def Const(self, source):
        s = 'init'
        
        try:
            s = source[self.index]
        # EOF 도달 시
        except EOFError:
            self.isEOF = True
            return
        
        # 작은 따옴표가 나올 때까지 토큰을 읽는다
        while(s != '’' or s != '‘'):
            self.token += s; self.index += 1
            
            try:
                s = source[self.index]
            # EOF 도달 시
            except EOFError:
                self.isEOF = True
                break
        # 닫기 전 새로운 여는 따옴표 만난다면   
        if(s == '‘'):
            self.index -= 1
            self.PrintError()
            
        elif(s == '‘'):
            self.PrintToken('tconst')
            self.token = '‘'
            self.PrintToken('OP')
        
        if(not self.isEOF):
            self.index += 1
        return
    

    # Zero State
    def Zero(self, source):
        try:
            s = source[self.index]
        # EOF 도달 시
        except EOFError:
            self.isEOF = True
        
        # 숫자 0
        if(s in self.TokTB.blank):
            self.PrintToken('tint')
            return

        # 0. 으로 시작하는 소수
        elif(s == '.'):
            self.token += s; self.index += 1
            self.RealNumber(source)     # 실수 State에서 처리
            return

        # 8진수 정수
        elif('1' <= s <= '7'):
            self.token += s; self.index += 1
            self.OctInt(source)         # 8진 정수 State에서 처리
            return

        # 0x 16진수 정수
        elif(s == 'x'):
            self.token += s; self.index += 1
            self.HexInt(source)         # 16진 State에서 처리
            return


    # 예약어 State
    def ReservedWord(self, source):
        result = True
        
        try:
            s = source[self.index]
        # EOF 도달 시
        except EOFError:
            tokNum = self.reservedTable.get(self.token)

            # 예약어 테이블에 있는 경우
            if(tokNum): self.PrintToken('tident')
            # 예약어 테이블에 없는 경우
            else:
                self.SymbolID(source)     # 심볼(식별자) State에서 처리
                return
            
            self.isEOF = True
            return

        # 공백 문자가 나올 때까지
        while(s not in self.TokTB.blank):
            if(result is False): pass      
            # 숫자 나올 시 심볼 테이블 참고
            elif('0'<= s <= '9'):
                self.index += 1
                self.SymbolID(source)       # 심볼(식별자) State에서 처리
                return
            
            # 특수 문자 or 연산자인 경우
            elif(s in self.TokTB.specialList or s in self.TokTB.opList):
                break
                
            # 알파벳, 숫자 이외의 문자 나올 시 토큰 인식 실패 처리
            elif(not ('a' <= s <= 'z' or 'A' <= s <= 'Z')):
                result = False
                
            self.token += s; self.index += 1
            
            try:
                s = source[self.index]
            except EOFError:        # EOF 도달 시
                self.isEOF = True
                break

        tokNum = self.TokTB.reservedTable.get(self.token)
        # 예약어 테이블에 있는 경우
        if(tokNum):
            self.PrintToken('Reserved')
        # 예약어 테이블에 없는 경우
        else:
            self.SymbolID(source)
            
        if(not self.isEOF):
            self.index += 1
        return

    # 심볼 State
    def SymbolID(self, source):
        result = True
        
        # 토큰이 소문자로 시작하는지 검사
        if(not 'a' <= self.token[0] <= 'z'):
            result = False
        
        try:
            s = source[self.index]
        # EOF 도달 시
        except EOFError:
            tokNum = self.TokTB.symbolTable.get(self.token)
            
            # 식별자 테이블에 있는 경우
            if(tokNum):
                self.PrintToken(self.token, 'tident')
            # 식별자 테이블에 없는 경우 새로 추가
            else:
                symTokNum = len(self.TokTB.symbolTable)
                self.TokTB.symbolTable[self.token] = symTokNum
                self.PrintToken('tident')
                
            self.isEOF = True
            return
                
        # 공백 문자가 나올 때까지
        while(s not in self.TokTB.blank):
            # 특수 문자 or 연산자인 경우
            if(s in self.TokTB.specialList or s in self.TokTB.opList):
                break
            
            # 숫자나 알파벳이 아닌 경우
            elif(not ('0'<= s <= '9' or 'a' <= s <= 'z' or 'A' <= s <= 'Z')):
                result = False
            
            self.token += s
            self.index += 1
                
            try:
                s = source[self.index]
            except EOFError:        # EOF 도달 시
                self.isEOF = True
                break
        
        # 토큰 출력    
        if(result):
            tokNum = self.TokTB.symbolTable.get(self.token)
            
            # 식별자 테이블에 있는 경우
            if(tokNum):
                self.PrintToken(self.token, 'tident')
            # 식별자 테이블에 없는 경우 새로 추가
            else:
                symTokNum = len(self.TokTB.symbolTable)
                self.TokTB.symbolTable[self.token] = symTokNum
                self.PrintToken('tident')
        else:
            self.PrintError()
            
        if(not self.isEOF):
            self.index += 1
        return


    # 10진 정수 State (0으로 시작 X 전제)
    def DecimalInt(self, source):
        result = True
        
        try:
            s = self.source[self.index]
        # EOF 도달 시
        except EOFError:
            self.PrintToken('tint')
            self.isEOF = True
            return
        
        # 공백이 나올 때까지    
        while(s not in self.TokTB.blank):
            if(result == False):
                pass

            elif(s < '0' or s > '9'):
                result = False

            elif(s == '.'):
                self.token += s; self.index += 1
                self.RealNumber(source)             # 실수 State에서 처리
                return
            
            elif(s == 'e'):
                self.token += s; self.index += 1
                self.FloatingRealNum(source)        # 부동 소수 State에서 처리     
                return
            
            self.token += s; self.index += 1
            try:
                s = source[self.index]
            # EOF 도달 시
            except EOFError:
                self.isEOF = True
                break
        
        # 토큰 메시지 출력
        if(result): self.PrintToken('tint')
        else:   self.PrintError()
        
        if(not self.isEOF):
            self.index += 1
        return
    
        
    # 8진 정수 State    (0d까지 읽은 상태)
    def OctInt(self, source):
        result = True
        
        try:
            s = self.source[self.index]
        # EOF 도달 시
        except EOFError:
            self.PrintToken('tint')
            self.isEOF = True
            return
        
        # 공백이 나올 때 까지
        while(s not in self.TokTB.blank):
            if(result is False):
                pass
            
            elif(s < '0' or s > '8'):
                result = False
                
            self.token += s
            self.index += 1
            
            try:
                s = self.source[self.index]
            # EOF 도달 시
            except EOFError:
                self.isEOF = True
                break
        
        # 토큰 메시지 출력
        if(result): self.PrintToken('tint')
        else: self.PrintError()
            
        if(not self.isEOF):
            self.index += 1
        return


    # 16진 정수 State   (0x 까지 읽은 상태)
    def HexInt(self, source):
        result = True
        
        try:
            s = source[self.index]
        # EOF 도달 시
        except EOFError:
            self.PrintToken('tint')
            self.isEOF = True
            return
        
        # 처음 x 다음에는 0이 아닌 숫자가 와야함
        # 0을 제외한 16진수의 심볼(1~9, A~F, a~f)에 의한 전이
        if(not ('1'<= s <='9' or 'A'<= s <='F' or 'a'<= s <='f')):
            result = False
        self.token += s
        self.index += 1
        
        try:
            s = source[self.index]
        # EOF 도달 시
        except EOFError:
            self.PrintToken('tint')
            self.isEOF = True
            return
        
        # 다음 공백까지
        while(s not in self.TokTB.blank):
            # 16진수의 심볼(1~9, A~F, a~f)에 의한 전이
            if(result is False): pass
            elif(not ('0'<= s <='9' or 'A'<= s <='F' or 'a'<= s <='f')):
                result = False
                
            self.token += s; self.index += 1
            
            try:
                s = source[self.index]
            # EOF 도달 시
            except EOFError:
                self.isEOF = True
                break
            
        # 토큰 메시지 출력
        if(result): self.PrintToken('tint')
        else: self.PrintError()
            
        if(not self.isEOF):
            self.index += 1
        return


    # 실수, 부동 실수 State (숫자. 까지 읽은 상태)
    def RealNumber(self, source):
        result = True
        isFloat = True
        
        # 0. 으로 시작하면 부동 소수점 표기 시의 유효 숫자 조건에 맞지 않으므로 전이 불가
        if(self.token =='0.'):
            isFloat = False
            
        try:
            s = source[self.index]
        # EOF 도달 시 에러 출력
        except EOFError:
            self.PrintError('treal')
            self.isEOF = True
            return
        
        # 공백이 나올 때까지 읽는다
        while(s not in self.TokTB.blank):
            if(result is False):
                pass
            # 부동 소수점 State 전이
            elif(s == 'e' and isFloat):
                self.token += s; self.index += 1
                self.FloatingRealNum(source)            # 부동 소수 State에서 처리
                return
                
            elif(not '0' <= s <= '9'):
                result is False
            
            self.token += s; self.index += 1
            
            try:
                s = source[self.index]
            # EOF 도달 시
            except EOFError:
                self.isEOF = True
                break
        
        # 토큰 메시지 출력
        if(result): self.PrintToken('treal')
        else: self.PrintError()
            
        if(not self.isEOF):
            self.index += 1
        return   
        

    # 숫자e 까지 읽은 상태
    def FloatingRealNum(self, source):
        result = True
        
        try:
            s = source[self.index]
        # EOF 도달 시 에러 메시지 출력
        except EOFError:
            self.PrintError('treal')
            self.isEOF = True
            return

        # +, - 부호 검사
        if(not (s == '+' or s == '-')):
            result = False

        self.token += s; self.index += 1
        
        # 공백이 나올 때까지 읽는다
        while(s not in self.TokTB.blank):
            if(result is False):
                pass
            elif(not '0' <= s <= '9'):
                result = False
                
            self.token += s; self.index += 1
            
            try:
                s = source[self.index]
            # EOF 도달 시 에러 메시지 출력
            except EOFError:
                self.isEOF = True
                break

        # 토큰 메시지 출력
        if(result): self.PrintToken('treal')
        else: self.PrintError()
            
        if(not self.isEOF):
            self.index += 1
        return   
                

    # 토큰 인식 메시지 출력하는 메소드
    def PrintToken(self, tokType):
        tokNum = 0
        
        # 예약어 테이블에서 토큰 출력
        if(tokType == 'Reserved'):
            tokNum = self.TokTB.reservedTable.get(self.token)
        
        # 심볼 테이블에서 토큰 출력    
        elif(tokType == 'tident'):
            tokNum = self.TokTB.symbolTable.get(self.token)
            
        # OP 테이블에서 토큰 출력
        elif(tokType == 'OP'):
            tokNum = self.TokTB.opTable.get(self.token)
        
        # 정수
        elif(tokType == 'tint'):
            tokNum = self.TokTB.opTable.get('tint')
        
        # 실수
        elif(tokType == 'treal'):
            tokNum = self.TokTB.opTable.get('treal')
        
        # 상수
        elif(tokType == 'tconst'):
            tokNum = self.TokTB.opTable.get('tconst')
        
        # 토큰 테이블에서 읽어오기 실패
        if(tokNum == 0 or tokNum is None):
            print(f"Failed to Read in Token table: {self.token}")
        else:
        # 토큰 인식 메시지 출력
            print(f"{self.token}: ({tokType}, {tokNum})   --> Success")  
        return

    
    # 토큰 인식 실패 메세지 출력하는 메소드
    def PrintError(self):
        print(f"{self.token} is Invalid   --> Failed")
        
    
    # 제거한 주석 출력하는 메소드    
    def PrintComment(self):
        print(f"Success to Remove Comment")
        print(f"{self.token}\n")
        

### 데이터 실행부

scanner = MiniCompiler()

f1 = 'GoodFile.txt'             # 정상 데이터
f2 = 'BadFile.txt'              # 오류 데이터

files = [f1, f2]

for fname in files:
    f = open(fname, 'rt', encoding='UTF8')
    source = f.read()

    print(f"Source: {fname}")
    print("="*15, "\n\n")
    scanner.Initial(source)