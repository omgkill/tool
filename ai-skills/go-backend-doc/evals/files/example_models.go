package model

import (
	"time"
	"gorm.io/gorm"
)

// User 用户表
type User struct {
	ID        uint      `gorm:"primaryKey" json:"id"`
	Username  string    `gorm:"uniqueIndex;size:50;not null" json:"username"`
	Password  string    `gorm:"size:255;not null" json:"-"`
	Email     string    `gorm:"uniqueIndex;size:100" json:"email"`
	Nickname  string    `gorm:"size:50" json:"nickname"`
	Level     int       `gorm:"default:1;index" json:"level"`
	Coins     int64     `gorm:"default:0" json:"coins"`
	Diamonds  int       `gorm:"default:0" json:"diamonds"`
	Status    int8      `gorm:"default:1;comment:1-正常,2-封禁" json:"status"`
	LastLogin time.Time `json:"last_login"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
	DeletedAt gorm.DeletedAt `gorm:"index" json:"-"`
}

// TableName 指定表名
func (User) TableName() string {
	return "users"
}

// GameRecord 游戏记录
type GameRecord struct {
	ID        uint      `gorm:"primaryKey" json:"id"`
	UserID    uint      `gorm:"index;not null" json:"user_id"`
	GameType  int       `gorm:"comment:游戏类型:1-竞速,2-闯关,3-对战" json:"game_type"`
	Score     int       `gorm:"not null" json:"score"`
	Duration  int       `gorm:"comment:游戏时长(秒)" json:"duration"`
	Coins     int64     `gorm:"comment:获得金币" json:"coins"`
	Status    int8      `gorm:"default:0;comment:0-进行中,1-已完成,2-已放弃" json:"status"`
	CreatedAt time.Time `gorm:"index" json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
	
	// 关联
	User User `gorm:"foreignKey:UserID" json:"user,omitempty"`
}

func (GameRecord) TableName() string {
	return "game_records"
}

// UserItem 用户道具
type UserItem struct {
	ID        uint      `gorm:"primaryKey" json:"id"`
	UserID    uint      `gorm:"index;not null" json:"user_id"`
	ItemID    uint      `gorm:"not null" json:"item_id"`
	Quantity  int       `gorm:"default:1" json:"quantity"`
	ExpireAt  *time.Time `json:"expire_at,omitempty"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
	
	// 关联
	User User `gorm:"foreignKey:UserID" json:"user,omitempty"`
	Item Item `gorm:"foreignKey:ItemID" json:"item,omitempty"`
}

func (UserItem) TableName() string {
	return "user_items"
}

// Item 道具模板
type Item struct {
	ID          uint   `gorm:"primaryKey" json:"id"`
	Name        string `gorm:"size:100;not null" json:"name"`
	Description string `gorm:"size:500" json:"description"`
	Type        int    `gorm:"comment:1-消耗品,2-装备,3-特殊道具" json:"type"`
	Price       int64  `gorm:"comment:金币价格" json:"price"`
	DiamondPrice int   `gorm:"comment:钻石价格" json:"diamond_price"`
	Effect      string `gorm:"type:json;comment:道具效果配置" json:"effect"`
	Status      int8   `gorm:"default:1;comment:1-上架,2-下架" json:"status"`
	CreatedAt   time.Time `json:"created_at"`
	UpdatedAt   time.Time `json:"updated_at"`
}

func (Item) TableName() string {
	return "items"
}
