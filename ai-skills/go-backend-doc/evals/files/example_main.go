package main

import (
	"log"
	"net/http"

	"github.com/gin-gonic/gin"
	"google.golang.org/grpc"
	
	"example.com/game/config"
	"example.com/game/handler"
	"example.com/game/service"
	pb "example.com/game/proto"
)

func main() {
	// 加载配置
	cfg := config.Load()
	
	// 初始化数据库
	db := initDB(cfg.Database)
	
	// 初始化 Redis
	rdb := initRedis(cfg.Redis)
	
	// 启动 gRPC 服务
	go startGRPCServer(cfg.GRPCPort, db, rdb)
	
	// 启动 HTTP 服务
	startHTTPServer(cfg.HTTPPort, db, rdb)
}

func startHTTPServer(port string, db *sql.DB, rdb *redis.Client) {
	r := gin.Default()
	
	// 用户相关路由
	userHandler := handler.NewUserHandler(db, rdb)
	r.POST("/api/v1/user/register", userHandler.Register)
	r.POST("/api/v1/user/login", userHandler.Login)
	r.GET("/api/v1/user/profile", userHandler.GetProfile)
	
	// 游戏相关路由
	gameHandler := handler.NewGameHandler(db, rdb)
	r.POST("/api/v1/game/start", gameHandler.StartGame)
	r.POST("/api/v1/game/submit", gameHandler.SubmitScore)
	r.GET("/api/v1/game/leaderboard", gameHandler.GetLeaderboard)
	
	log.Printf("HTTP server listening on :%s", port)
	r.Run(":" + port)
}

func startGRPCServer(port string, db *sql.DB, rdb *redis.Client) {
	lis, err := net.Listen("tcp", ":"+port)
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}
	
	s := grpc.NewServer()
	
	// 注册 gRPC 服务
	userService := service.NewUserService(db, rdb)
	pb.RegisterUserServiceServer(s, userService)
	
	gameService := service.NewGameService(db, rdb)
	pb.RegisterGameServiceServer(s, gameService)
	
	log.Printf("gRPC server listening on :%s", port)
	if err := s.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}
