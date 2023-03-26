CREATE TRIGGER delete_cart_items AFTER INSERT ON orders
FOR EACH ROW
    DELETE FROM carts
    WHERE orderid = NEW.orderid;


CREATE TRIGGER delete_seller_products AFTER DELETE ON sellers
FOR EACH ROW
    DELETE FROM products
    WHERE sellerid = OLD.sellerid;